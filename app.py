"""
EV Charging Locator - Backend (Python + Flask)

Run:  python app.py   then open http://127.0.0.1:5000
"""
from math import radians, sin, cos, asin, sqrt
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# 1. SAMPLE DATA (approximate locations in Chennai - for learning/demo only).
#    Later, replace this list with data from the Open Charge Map API.
# ---------------------------------------------------------------------------
STATIONS = [
    {"id": 1, "name": "Tata Power EZ Charge - Phoenix Marketcity", "area": "Velachery",
     "lat": 12.9906, "lng": 80.2168, "connectors": ["CCS2", "Type 2"], "power_kw": 60},
    {"id": 2, "name": "Statiq - Express Avenue", "area": "Royapettah",
     "lat": 13.0587, "lng": 80.2647, "connectors": ["CCS2", "Type 2"], "power_kw": 30},
    {"id": 3, "name": "ChargeZone - T. Nagar", "area": "T. Nagar",
     "lat": 13.0418, "lng": 80.2341, "connectors": ["CCS2", "CHAdeMO"], "power_kw": 50},
    {"id": 4, "name": "Tata Power - Airport", "area": "Meenambakkam",
     "lat": 12.9941, "lng": 80.1709, "connectors": ["CCS2"], "power_kw": 120},
    {"id": 5, "name": "Ather Grid - Anna Nagar", "area": "Anna Nagar",
     "lat": 13.0850, "lng": 80.2101, "connectors": ["Type 2"], "power_kw": 7},
    {"id": 6, "name": "Jio-bp Pulse - OMR", "area": "Sholinganallur",
     "lat": 12.9010, "lng": 80.2279, "connectors": ["CCS2", "Type 2"], "power_kw": 60},
    {"id": 7, "name": "Statiq - Adyar", "area": "Adyar",
     "lat": 13.0067, "lng": 80.2570, "connectors": ["Type 2", "CHAdeMO"], "power_kw": 22},
    {"id": 8, "name": "ChargeZone - Guindy", "area": "Guindy",
     "lat": 13.0067, "lng": 80.2206, "connectors": ["CCS2"], "power_kw": 50},
    {"id": 9, "name": "EVRE - Porur", "area": "Porur",
     "lat": 13.0382, "lng": 80.1565, "connectors": ["Type 2"], "power_kw": 11},
    {"id": 10, "name": "Tata Power - Besant Nagar", "area": "Besant Nagar",
     "lat": 13.0002, "lng": 80.2668, "connectors": ["CCS2", "Type 2"], "power_kw": 30},
]

FAST_CHARGER_KW = 25  # anything at or above this counts as "fast"


# ---------------------------------------------------------------------------
# 2. HAVERSINE FORMULA - distance in km between two latitude/longitude points
# ---------------------------------------------------------------------------
def haversine_km(lat1, lng1, lat2, lng2):
    earth_radius_km = 6371
    d_lat = radians(lat2 - lat1)
    d_lng = radians(lng2 - lng1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lng / 2) ** 2
    return 2 * earth_radius_km * asin(sqrt(a))


# ---------------------------------------------------------------------------
# 3. ROUTES
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/stations")
def get_stations():
    """
    Query parameters (all optional):
      lat, lng       -> user location; adds 'distance_km' and sorts nearest first
      connector      -> e.g. CCS2, Type 2, CHAdeMO
      fast_only      -> 'true' to show only fast chargers
    """
    connector = request.args.get("connector", "").strip()
    fast_only = request.args.get("fast_only", "false").lower() == "true"
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)

    results = []
    for station in STATIONS:
        if connector and connector not in station["connectors"]:
            continue
        if fast_only and station["power_kw"] < FAST_CHARGER_KW:
            continue

        item = dict(station)  # copy so the original list is not changed
        item["is_fast"] = station["power_kw"] >= FAST_CHARGER_KW
        if lat is not None and lng is not None:
            item["distance_km"] = round(haversine_km(lat, lng, station["lat"], station["lng"]), 1)
        results.append(item)

    if lat is not None and lng is not None:
        results.sort(key=lambda s: s["distance_km"])

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)