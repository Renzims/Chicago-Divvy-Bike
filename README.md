# 📝 Introduction

The **Cyclistic Bike Share Case Study** is a capstone project for the **Google Data Analytics Professional Certificate** on Coursera. In this project, I will follow the data analysis process which I learned from the course: ask, prepare, process, analyze, share and act to analyze the data.
# 💬 Background

Cyclistic is a **bike-share company** based in Chicago that launched a successful bike-sharing program in 2016. Throughout the years, the program has expanded significantly to a fleet of 5,824 bicycles and a network of 692 geotracked stations sprawled across the city. With the large number of bicycles across numerous stations, customers can rent bikes from one station and return them to any other station within the network at their convenience. This encourages people to opt for cycling as a mode of transportation, therefore contributing to the success of Cyclistic's bike-sharing program.

Cyclistic's marketing strategy has so far focused on building general awareness and appealing to broad consumer segments. The company offers flexibile pricing plans that cater to diverse needs of users including single-ride passes, full-day passes, and annual memberships. Besides, it provides reclining bikes, hand tricycles, and cargo bikes, effectively welcoming individuals with disabilities and those who can't ride on the standard two-wheeled bicycles. Based on the company database, Cyclistic users are more likely to ride for leisure, but about 30% use them to commute to work each day. While traditional bikes remain as the popular option, around 8% of users opt for the assistive alternatives.

The company's marketing director believes that the company’s future success depends on maximizing the number of annual memberships. Therefore, as a junior data analyst, my team and I have to understand how casual riders and annual members use Cyclistic bikes differently. From these insights, we will design a new marketing strategy to convert casual riders into annual members.
# ⚙ Approach/Steps

## 1. Ask
### 🎯 Business Task
The main goal is to **understand how annual members and casual riders use Cyclistic bikes differently**.  This insight will help the marketing team develop strategies to **convert casual riders into annual members**, increasing long-term profitability. 
### 👥 Key Stakeholders  
- **Lily Moreno** — Director of Marketing, responsible for campaign development and user acquisition.  
- **Cyclistic Marketing Analytics Team** — Collects and analyzes data to guide strategic decisions.  
- **Cyclistic Executive Team** — Approves marketing strategies based on analytical insights.
### ❓ Guiding Questions 
1. **How do annual members and casual riders use Cyclistic bikes differently? (The main question of this analytical project)** 
2. Why would casual riders buy Cyclistic annual memberships?
3. How can Cyclistic use digital media to influence casual riders to become members?
### 🧩 Key Tasks  
- Identify and clearly define the **business problem** - Determine how annual members and casual riders use Cyclistic bikes differently to inform data-driven marketing strategies aimed at increasing membership conversions..  

****
## 2. Prepare
### 🗂️ Data Source  
The dataset used for this analysis was provided by **Motivate International Inc.** and made available for public use.  
Although the fictional company in this case is *Cyclistic*, the real-world data comes from **Divvy Bikes (Chicago)**.  

- **Dataset:** [Divvy Trip Data](https://divvy-tripdata.s3.amazonaws.com/index.html)  
- **License:** [Data License Agreement](https://www.divvybikes.com/data-license-agreement)  
- **Timeframe:** 12 months (January–December 2024)  
- **File format:** `.csv` (monthly files)  
- **Data size:** ~ 5.8 million rows across 12 files  
- **Privacy note:** No personally identifiable information is included (PII removed).  
### 🧩 Data Description  
Each dataset contains detailed information about every bike trip, including:  

| Column               | Description                                                   |
| -------------------- | ------------------------------------------------------------- |
| `ride_id`            | Unique identifier for each trip                               |
| `rideable_type`      | Type of bike (`classic_bike`, `docked_bike`, `electric_bike`) |
| `started_at`         | Start date and time of the ride                               |
| `ended_at`           | End date and time of the ride                                 |
| `start_station_name` | Name of the station where the trip started                    |
| `start_station_id`   | ID of the station where the trip started                      |
| `end_station_name`   | Name of the station where the trip ended                      |
| `end_station_id`     | ID of the station where the trip ended                        |
| `start_lat`          | Latitude of the start station                                 |
| `start_lng`          | Longitude of the start station                                |
| `end_lat`            | Latitude of the end station                                   |
| `end_lng`            | Longitude of the end station                                  |
| `member_casual`      | Type of user (`member` or `casual`)                           |

****
## 3. Process
### 🧠 Objective  
Prepare the Cyclistic dataset for analysis by cleaning, transforming, and validating the data to ensure accuracy and consistency.  
This stage ensures that all data is structured and ready for analysis in Python and Tableau.
### 🧰 Tools Used  
* **Python** - Data transformation and cleaning
* **Tableau** - Final analysis and visualization
### 🧹 Data Process Steps  
1. **Load monthly CSV files**  
   Combined 12 monthly `.csv` files (Jan–Dec 2024) into a single dataset using Python.
2. **Convert data types**  
   Changed columns `started_at` and `ended_at` to datetime format for duration calculation.
3. **Check and remove duplicates**  
   Verified unique `ride_id` values and removed rows
4. **Impossible time**  
   Removed lines where the trip start time was greater than the trip end time.
5. **Lost geographic data**  
   Deleted all records where end_station_name, end_station_id, end_lat, end_lng were simultaneously missing
6. **Geographic limitations**  
   All lines were analyzed for exceeding Chicago city limits. Trip endpoints were especially important due to their impossible values.
7. **Feature Extraction**  
   Based on the basic data that was presented in the data set, the following attributes were created: trip_duration, month, day, day_of_week, trip_distance, speed, time_of_day, holiday_name and creating routes datasets
8. **Statistical analysis and data removal**  
   Using the Interquartile range method to find anomalies in the data, cleaned the attributes trip_duration, trip_distance, and speed (calculated separately for conventional and electric modes of transport) based on their logarithmic transformation.
## 4. Analyze
### 1. Ride Characteristics — Duration, Distance, and Speed  
- **Members** tend to have **shorter trips** but move at a **higher average speed** (≈12.5–19.5% faster).  
- **Casual riders** prefer **longer and slower rides**, focusing on leisure rather than commuting.  
- **Rideable type analysis:**  
  - No significant difference in transport type usage between user groups.  
  - For `electric_bike` and `electric_scooter`, distance differs by only ~2.5%.  
  - For `classic_bike`, casual riders travel **14.4% farther** but **19.4% slower**.  
  - Average ride duration: casual rides are **10–12% longer** on electric vehicles and **35.6% longer** on classic bikes.  
### 2. Seasonality and Weather Impact  
- **Members:** Show steady year-round usage with gradual decline from summer to winter → consistent commuters.  
- **Casuals:** Strong seasonal pattern — **4× drop in winter vs spring** → weather-sensitive leisure riders.  
- **Statistical trend:**  
  - In summer, casuals’ average trip duration is **23–24% longer**, distance **6–7% greater**, and members’ speed **15–17% higher**.  
  - Minimal seasonal variation for members → routine use; large variation for casuals → weather-dependent behavior.  
- **Monthly peaks:** May–October shows the highest casual activity.  
  - Speed dips in November (cooler weather).  
  - January — lowest ride frequency and minimal group differences.
### 3. Weekly Patterns  
- **Members:** Stable usage across weekdays, with a decline during weekends (from ~14–17% to 11–12%).  
- **Casuals:** Opposite pattern — weekdays at 12–13%, weekends and Fridays surge to **15–20%**.  
- **Ride statistics:**  
  - Little difference on weekdays.  
  - On weekends and Fridays, casuals ride **slower and longer**, confirming a recreational pattern.
### 4. Time of Day Analysis  
- Both groups peak in the **evening**, but with distinct patterns:  
  - **Members:** Gradual decline from morning to night; minimal use after 22:00.  
  - **Casuals:** Evening (37.2%) and daytime (32.9%) dominate; higher night usage (after 22:00).  
- **Statistical differences:**  
  - Midday shows the strongest contrast — **speed 20% lower** and **distance 15% shorter** for casuals.  
  - Other time slots differ by ≤14% in speed and ≤5% in distance.  
### 5. Spatial Distribution (Station Usage)  
- **Members:**  
  - More **diverse distribution**, concentrated in the **business district** and nearby residential zones. 
  - Top stations include central areas near offices and transport hubs (≈28K rides).  
- **Casuals:**  
  - Strong **coastal concentration** — popular spots along the lakefront.  
  - One top station near the waterfront reaches **35K rides**.  
### 6. Temporal & Spatial Patterns Combined  
- **By time of day:**  
  - Members: morning trips start and end mostly in the business center.  
  - Casuals: consistent waterfront dominance throughout the day.  
- **By weekday:**  
  - Members follow the weekday commuting pattern; weekends resemble casual activity.  
  - Casuals maintain waterfront dominance on weekends and Fridays.  
- **By season:**  
  - Members: minor shift toward the waterfront in summer.  
  - Casuals: reduced waterfront usage in fall/winter due to weather.  
### 7. Route Analysis  
- **Members:** exhibit a **diverse route network** — combining city center trips with outer-district destinations.  
- **Casuals:** show **cyclical and repetitive routes**, especially along the waterfront loop.  
## 5. Share
### 🔗 Tableau Data Story  
**Interactive Story:** [Divvy Chicago Bike Analysis — by Ivan Honchar](https://public.tableau.com/app/profile/ivan.honcahr/viz/DivvyChicagoBikeAnalysis/Story1)
### 📊 Key Visual Insights  
#### 🏁 Key KPIs 
![alt text](<Dashboard/Story 1.png>)
- **Member users:** Higher speed, shorter trips, efficient commuting.  
- **Casual users:** Slower pace, rides last **~28% longer**, emphasizing leisure.  
- **Similarity:** Distance traveled nearly identical (<10% difference), confirming consistent trip scale across groups.
#### 🕒 Temporal Trends  
![alt text](<Dashboard/Story 2.png>)

| Member Users | Casual Users |
|---------------|---------------|
| Stable usage year-round. | Sharp summer peaks, winter declines. |
| Minimal seasonal changes except weekends. | 4× higher summer activity vs winter. |
| Weekday-focused, commuting-driven. | Weekend and holiday-focused, leisure-driven. |
#### 🗺️ Spatial Distribution  
![alt text](<Dashboard/Story 3.1.png>)
![alt text](<Dashboard/Story 3.2.png>)

| Member Users                                     | Casual Users                                                           |
| ------------------------------------------------ | ---------------------------------------------------------------------- |
| Stations centered around **business districts**. | Stations clustered near **tourist and coastal areas** (Lake Michigan). |
| Balanced station popularity across zones.        | Sharp drop in usage with distance from the waterfront.                 |

#### 🧭 Route Patterns  
![alt text](<Dashboard/Story 4.1.png>)
![alt text](<Dashboard/Story 4.2.png>)

| Member Users | Casual Users |
|---------------|---------------|
| Main routes connect **residential → business areas**. | Main routes run **along the lakefront and downtown**. |
| Trips reflect daily commute behavior. | Trips reflect recreational, sightseeing, and tourist activity. |
#### 🔍 Key Behavioral Differences  
| Member Users | Casual Users |
|---------------|---------------|
| Daily commuters with consistent weekday use. | Tourists and leisure users with weekend focus. |
| Stable usage both weekly and yearly. | Seasonal fluctuations, peaking in summer. |
| Short, quick rides for transportation. | Long, slow rides for recreation. |
| Interest areas: **residential and business zones**. | Interest areas: **tourist and waterfront zones**. |
