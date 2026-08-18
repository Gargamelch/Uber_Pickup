---
title: Uber NYC Hot Zones
emoji: 🚕
colorFrom: blue
colorTo: purple
sdk: docker
app_file: app.py
pinned: false
license: gpl-3.0
---

<img src="https://upload.wikimedia.org/wikipedia/commons/5/58/Uber_logo_2018.svg" alt="Uber logo" width="200" />

# NYC Uber Hot-Zone Detection

Find where Uber riders are most needed across New York City. We break this down by day of the week and time of day, so drivers can go to busy areas before riders have to wait too long.

## Project goal

In NYC, Uber riders sometimes wait 10 to 15 minutes for a ride. People usually start **canceling after 5 to 7 minutes** of waiting. This project creates an algorithm to find **hot zones** (areas where lots of people are requesting rides) for each time slot, and shows them on interactive maps.
It also provide an interactive dashboard showing where Uber demand concentrates across New York City. Find hot zones by day of week and hour to help drivers position themselves strategically.

## Live Demo

**Try the dashboard:** [Click here to access the Streamlit dashboard](https://huggingface.co/spaces/xxx)


## Data

| File | Rows | Description |
|---|---|---|
| `uber-raw-data-{apr,may,jun,jul,aug,sep}14.csv` | ~4.5M | Raw 2014 pickups: `Date/Time, Lat, Lon, Base` |
| `uber-raw-data-janjune-15.csv` | ~14.3M | 2015 pickups tagged by zone ID instead of coordinates |
| `taxi-zone-lookup.csv` | 265 | Reference table mapping `LocationID` → `Borough`/`Zone` |

Source: [Uber Trip Data](https://full-stack-bigdata-datasets.s3.eu-west-3.amazonaws.com/Machine+Learning+non+Supervis%C3%A9/Projects/uber-trip-data.zip)

## Approach


1. **Clean the Data**: Remove pickup locations outside NYC's official boundaries (about 0.76% of rows were GPS errors and got removed).

2. **Start Small**: Test the clustering method on one busy hour first. Use KMeans clustering and figure out the right number of clusters using the "elbow method" and silhouette score.

3. **Scale Up**: Run the clustering separately for all 168 time slots (7 days × 24 hours). Create a lookup table with cluster centers and how many pickups are in each area.

4. **Make Maps**: Build interactive Plotly maps showing the clusters and their center points, plus heatmaps showing demand patterns by day and hour.

5. **Double-Check**: Compare the 2014 location-based results with the 2015 zone-based data to see if they match for the same times.


## Usage

Open and run `Uber_Pickups.ipynb` top to bottom. Key outputs:

- **`hotzones_summary.csv`**: One row for each cluster, for each time slot, with center coordinates and pickup counts. Use this in a driver app: check the current day and hour to get a list of hot zones ranked by demand.

- **`pickups_with_clusters.csv`**: All 2014 pickups, each tagged with its cluster assignment

## Results

- Demand changes more than 20x during the week, from about 2,500 pickups at the slowest hour to around 56,000 at the busiest hour.

- Setting **k=9 clusters** worked well for all 168 time slots (chosen using elbow + silhouette analysis).

- The hot zones from 2014 line up with the busiest zones in 2015 data. Midtown Manhattan, Upper East Side, JFK Airport, and LaGuardia Airport all appear as hot zones using both methods.

## Tech stack

- **pandas / numpy**: Load and process the data
- **scikit-learn**: KMeans clustering, data scaling, cluster quality checks
- **Plotly**: Interactive maps and charts

## Limitations & next steps

- The 2015 cross-check uses zones, not exact coordinates, so we can confirm which neighborhoods are busy but not pinpoint exact spots within them.

- We kept k=9 for all time slots instead of adjusting per slot. This works well since demand levels are similar across all slots, but it could be fine-tuned.
