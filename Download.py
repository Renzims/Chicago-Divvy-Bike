import argparse
import re
import zipfile
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

DIVVY_INDEX = "https://divvy-tripdata.s3.amazonaws.com/index.html"
CHICAGO_CITY_GEOJSON = "https://data.cityofchicago.org/api/geospatial/ewy2-6yfk?method=export&format=GeoJSON"
YEAR = 2024
DIVVY_FILE_RE = re.compile(rf"{YEAR}\d{{2}}-divvy-tripdata\.(zip|csv|parquet)$", re.IGNORECASE)


def list_divvy_year_files(index_url: str) -> list[str]:
    r = requests.get(index_url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    urls = set()
    for a in soup.find_all("a", href=True):
        url = urljoin(index_url, a["href"])
        if DIVVY_FILE_RE.search(url):
            urls.add(url)

    def month_key(u: str):
        m = re.search(rf"{YEAR}(\d{{2}})-divvy-tripdata", u)
        return int(m.group(1)) if m else 99

    return sorted(urls, key=month_key)


def human_size(n: int) -> str:
    size = float(n)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}PB"


def download_file(url: str, out_path: Path, overwrite: bool = False) -> Path:
    if out_path.exists() and not overwrite:
        print(f"✔ It already exists: {out_path.name}")
        return out_path

    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        desc = f"↓ {out_path.name}"
        with open(out_path, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=desc) as bar:
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
        print(f"📦 Unpacked: {zip_path.name} → {out_dir}")
    except zipfile.BadZipFile:
        print(f"⚠️ Corrupted archive: {zip_path.name}")


def fetch_divvy(year_dir: Path, months: list[int] | None, overwrite: bool):
    """Downloads all Divvy files for the year and unzips ZIP files"""
    urls = list_divvy_year_files(DIVVY_INDEX)
    if months:
        urls = [u for u in urls if int(re.search(rf"{YEAR}(\d{{2}})", u).group(1)) in months]

    print(f"Found Divvy files for {YEAR}: {len(urls)}\n")

    for url in urls:
        file_name = url.split("/")[-1]
        dest = year_dir / file_name
        file_path = download_file(url, dest, overwrite=overwrite)

        # если это ZIP — распакуем
        if file_path.suffix.lower() == ".zip":
            extract_zip(file_path, year_dir)


def fetch_city_geojson(external_dir: Path, overwrite: bool):
    out = external_dir / "Boundaries_City_Chicago.geojson"
    if out.exists() and not overwrite:
        print(f"✔ GeoJSON already downloaded: {out.name}")
        return
    r = requests.get(CHICAGO_CITY_GEOJSON, timeout=30)
    r.raise_for_status()
    out.write_bytes(r.content)
    print(f"✔ Downloaded GeoJSON: {out} ({human_size(out.stat().st_size)})")


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
    ap = argparse.ArgumentParser(description="Downloads Divvy 2024 and GeoJSON for the city of Chicago (without creating folders)")
    ap.add_argument("--raw", default="data/raw/2024", help="Folder for Divvy CSV/ZIP files")
    ap.add_argument("--external", default="data/external", help="Folder for GeoJSON")
    ap.add_argument("--months", default="", help="Months (e.g. '1-3' or '1,7,12')")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    args = ap.parse_args()

    raw_dir = Path(args.raw).resolve()
    external_dir = Path(args.external).resolve()

    if not raw_dir.exists() or not external_dir.exists():
        print(f"❌ Error: One of the folders was not found.\n"
              f"Make sure the following exist:\n  {raw_dir}\n  {external_dir}")
        return

    months = parse_months_arg(args.months)
    fetch_divvy(raw_dir, months, overwrite=args.overwrite)
    fetch_city_geojson(external_dir, overwrite=args.overwrite)

    print("\n✅ All files successfully downloaded and extracted.")


if __name__ == "__main__":
    main()
