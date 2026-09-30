# Fuel Route Planner API

Django 6.1 API that plans a USA driving route and picks cost-effective fuel stops from the provided OPIS truck-stop price list.

## Features

- Accepts `start` and `finish` as free-text addresses **or** `lat,lon`
- One OSRM routing call for the full drive geometry (free, no API key)
- Nominatim geocoding only when addresses are used (0–2 calls)
- In-memory KD-tree over ~6.5k geocoded stations for fast corridor search
- Cost-effective fuel stops for a **500-mile** range vehicle at **10 MPG**
- Returns route GeoJSON, fuel stops, and total fuel cost

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py build_station_cache
python manage.py runserver
```

## API

### `GET/POST /api/route/`

Parameters (query string or JSON body):

| Name | Description |
|------|-------------|
| `start` | Origin address or `lat,lon` |
| `finish` | Destination address or `lat,lon` |

Example (coordinates — **1 external call** to OSRM):

```bash
curl "http://127.0.0.1:8000/api/route/?start=35.4676,-97.5164&finish=41.8781,-87.6298"
```

Example (addresses — up to **3 external calls**: 2× Nominatim + 1× OSRM):

```bash
curl "http://127.0.0.1:8000/api/route/?start=Oklahoma%20City,%20OK&finish=Chicago,%20IL"
```

## Response fields

- `route.geometry` — GeoJSON LineString of the driving route
- `map` — GeoJSON FeatureCollection (route line + start/finish + fuel-stop points)
- `fuel_stops[]` — ordered stops with price, gallons, cost, and route mile
- `total_fuel_cost_usd` — money spent on fuel for the trip at 10 MPG
- `total_gallons` — gallons required for the trip

## Design notes

- **Routing:** [OSRM](https://project-osrm.org/) public demo server `router.project-osrm.org`
- **Geocoding (start/finish addresses):** [Nominatim](https://nominatim.openstreetmap.org/)
- **Station locations:** the fuel CSV has no lat/lon, so stations are joined once to US city centroids in `data/us_cities.csv` and cached in `data/stations_cache.pkl`
- **Fuel strategy:** fill at the cheapest station in the first tank window, then whenever the destination is still out of range, stop at the cheapest reachable station and top up; total gallons ≈ `distance_miles / 10`
