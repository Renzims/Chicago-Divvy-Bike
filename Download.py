import argparse
import re
import zipfile
import time
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from tqdm import tqdm

DIVVY_BUCKET = "https://divvy-tripdata.s3.amazonaws.com"
SOCRATA_GEOJSON_RESOURCE = "https://data.cityofchicago.org/resource/qqq8-j68g.geojson"
YEAR = 2024
DIVVY_FILE_RE = re.compile(rf"^{YEAR}\d{{2}}-divvy-tripdata\.(zip|csv|parquet)$", re.IGNORECASE)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; DivvyFetcher/1.0; +https://example.org)",
    "Accept": "application/geo+json, application/json;q=0.9, */*;q=0.1",
}

def get_with_retries(url: str, stream: bool = False, timeout: int = 60, attempts: int = 3) -> requests.Response:
    last_exc = None
    for i in range(1, attempts + 1):
        try:
            r = requests.get(url, headers=HEADERS, stream=stream, timeout=timeout, allow_redirects=True)
            r.raise_for_status()
            return r
        except Exception as e:
            last_exc = e
            if i < attempts:
                time.sleep(1.5 * i)
            else:
                raise
    raise last_exc

def human_size(n: int) -> str:
    size = float(n)
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}EB"

def looks_like_geojson_bytes(b: bytes) -> bool:
    try:
        obj = json.loads(b.decode("utf-8", errors="replace"))
        return isinstance(obj, dict) and "type" in obj
    except Exception:
        return False

def list_divvy_year_files(bucket_url: str, year: int = YEAR) -> list[str]:
    prefix = f"{year}"
    urls, continuation = [], None
    while True:
        q = f"list-type=2&prefix={quote(prefix)}"
        if continuation:
            q += f"&continuation-token={quote(continuation)}"
        url = f"{bucket_url}/?{q}"

        r = get_with_retries(url, stream=False, timeout=30, attempts=3)
        root = ET.fromstring(r.content)

        for key_el in root.findall(".//{*}Contents/{*}Key"):
            key = (key_el.text or "").strip()
            if not key:
                continue
            name = key.split("/")[-1]
            if DIVVY_FILE_RE.search(name):
                urls.append(f"{bucket_url}/{key}")

        is_truncated_el = root.find(".//{*}IsTruncated")
        is_truncated = (is_truncated_el is not None and is_truncated_el.text == "true")
        if not is_truncated:
            break
        token_el = root.find(".//{*}NextContinuationToken")
        continuation = token_el.text if token_el is not None else None
        if not continuation:
            break

    def month_key(u: str):
        m = re.search(rf"{year}(\d{{2}})-divvy-tripdata", u, flags=re.IGNORECASE)
        return int(m.group(1)) if m else 99

    return sorted(urls, key=month_key)

def download_file(url: str, out_path: Path, overwrite: bool = False) -> Path:
    if out_path.exists() and not overwrite:
        print(f"✔ It already exists: {out_path.name}")
        return out_path

    with get_with_retries(url, stream=True, timeout=90, attempts=3) as r:
        total_hdr = r.headers.get("content-length")
        try:
            total = int(total_hdr) if total_hdr is not None else 0
        except ValueError:
            total = 0

        desc = f"↓ {out_path.name}"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "wb") as f, tqdm(
            total=total if total > 0 else None, unit="B", unit_scale=True, desc=desc
        ) as bar:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))

    print(f"✔ Downloaded: {out_path.name} ({human_size(out_path.stat().st_size)})")
    return out_path

def extract_zip(zip_path: Path, out_dir: Path):
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(out_dir)
        print(f"📦 Extracted: {zip_path.name} → {out_dir}")
        zip_path.unlink(missing_ok=True)
        print(f"🗑️ Deleted zip: {zip_path.name}")
    except zipfile.BadZipFile:
        print(f"⚠️ Corrupted archive: {zip_path.name}")

def fetch_divvy(out_dir: Path, months: list[int] | None, overwrite: bool, workers: int = 4):
    urls = list_divvy_year_files(DIVVY_BUCKET, YEAR)
    if months:
        urls = [u for u in urls if int(re.search(rf"{YEAR}(\d{{2}})", u).group(1)) in months]

    print(f"Found Divvy files for {YEAR}: {len(urls)}\n")
    if not urls:
        print("⚠️ No files found. Check your connection or naming pattern..")
        return

    def _job(url: str):
        file_name = url.split("/")[-1]
        dest = out_dir / file_name
        file_path = download_file(url, dest, overwrite=overwrite)
        if file_path.suffix.lower() == ".zip":
            extract_zip(file_path, out_dir)
        return file_name

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_job, u): u for u in urls}
        for fut in as_completed(futures):
            try:
                fut.result()
            except Exception as e:
                print(f"⚠️ Error downloading {futures[fut]}: {e}")

def fetch_city_geojson(out_dir: Path, overwrite: bool, export_basename: str | None):
    if export_basename:
        fname = export_basename if export_basename.lower().endswith(".geojson") else f"{export_basename}.geojson"
    else:
        fname = "Boundaries_City_Chicago.geojson"
    out = out_dir / fname

    if out.exists() and not overwrite:
        print(f"✔ GeoJSON already downloaded: {out.name}")
        return

    resource_url = f"{SOCRATA_GEOJSON_RESOURCE}?$limit=500000"
    try:
        r1 = get_with_retries(resource_url, stream=False, timeout=60, attempts=3)
        data1 = r1.content
        if looks_like_geojson_bytes(data1):
            out.write_bytes(data1)
            print(f"✔ Downloaded GeoJSON (resource): {out} ({human_size(out.stat().st_size)})")
            return
        else:
            print("⚠️ Resource endpoint returned non-GeoJSON, trying geospatial export...")
    except Exception as e:
        print(f"⚠️ Resource endpoint failed: {e}. Trying geospatial export...")

    try:
        r2 = get_with_retries(SOCRATA_GEOSPATIAL_EXPORT, stream=False, timeout=60, attempts=3)
        data2 = r2.content
        if looks_like_geojson_bytes(data2):
            out.write_bytes(data2)
            print(f"✔ Downloaded GeoJSON (geospatial export): {out} ({human_size(out.stat().st_size)})")
            return
        else:
            raise RuntimeError("Geospatial export returned non-GeoJSON payload")
    except Exception as e:
        print(f"❌ Failed to download valid GeoJSON from both endpoints: {e}")
        raise

def parse_months_arg(arg: str | None) -> list[int] | None:
    if not arg:
        return None
    months = set()
    for part in arg.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-")
            months.update(range(int(a), int(b) + 1))
        else:
            months.add(int(part))
    return sorted(m for m in months if 1 <= m <= 12)

def main():
    ap = argparse.ArgumentParser(description="Downloads Divvy 2024 and City Boundaries GeoJSON into data/raw")
    ap.add_argument("--out", default="data", help="Base data folder (default: data)")
    ap.add_argument("--months", default="", help="Limit months, e.g. '1-3' or '1,7,12'")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    ap.add_argument("--workers", type=int, default=4, help="Parallel Divvy downloads (default: 4)")
    ap.add_argument("--city-export-name", default="Boundaries_-_City_20251109",
                    help="Filename (without or with .geojson) to save the city boundaries export; default: Boundaries_-_City_20251109")
    args = ap.parse_args()

    base_dir = Path(args.out).resolve()
    raw_dir = base_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Using data directory: {raw_dir}")

    months = parse_months_arg(args.months)

    with ThreadPoolExecutor(max_workers=2) as ex:
        fut_divvy = ex.submit(fetch_divvy, raw_dir, months, args.overwrite, args.workers)
        fut_geo = ex.submit(fetch_city_geojson, raw_dir, args.overwrite, args.city_export_name)
        fut_divvy.result()
        fut_geo.result()

    print("\n✅ Downloads complete.")
    print(f"📁 Base folder: {base_dir}")
    print(f"📂 Raw folder: {raw_dir}")
    print(f"📅 Months: {months if months else 'All'}")
    print(f"🗺️ City export name: {args.city_export_name if args.city_export_name else 'Boundaries_City_Chicago'}")
    print(f"🔄 Overwrite: {'Yes' if args.overwrite else 'No'}")
    print(f"👥 Workers: {args.workers}")

if __name__ == "__main__":
    main()
