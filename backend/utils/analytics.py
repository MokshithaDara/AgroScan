from collections import Counter, defaultdict
from datetime import datetime, timedelta

from database import scans_collection
from utils.location import get_coordinates

GEO_CACHE = {}


def _safe_date(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return None


def _coords_for_location(location):
    if location in GEO_CACHE:
        return GEO_CACHE[location]
    try:
        GEO_CACHE[location] = get_coordinates(location)
    except Exception:
        GEO_CACHE[location] = (None, None)
    return GEO_CACHE[location]


def get_hotspot_analytics(user_id, limit=300):
    if scans_collection is None:
        return {
            "total_scans": 0,
            "hotspots": [],
            "clusters": [],
            "district_trends": [],
            "top_diseases": [],
            "weekly_trend": [],
        }

    rows = list(
        scans_collection.find({"user_id": user_id}, {"_id": 0})
        .sort("date", -1)
        .limit(limit)
    )

    if not rows:
        return {
            "total_scans": 0,
            "hotspots": [],
            "clusters": [],
            "district_trends": [],
            "top_diseases": [],
            "weekly_trend": [],
        }

    by_location = defaultdict(list)
    disease_counter = Counter()
    by_week = Counter()

    for row in rows:
        loc = row.get("location", "Unknown")
        disease = row.get("disease", "Unknown")
        by_location[loc].append(row)
        disease_counter[disease] += 1
        dt = _safe_date(row.get("date"))
        if dt:
            by_week[f"{dt.isocalendar().year}-W{dt.isocalendar().week:02d}"] += 1

    hotspots = []
    cluster_counter = defaultdict(int)
    for location, records in by_location.items():
        lat, lon = _coords_for_location(location)
        disease_counts = Counter(r.get("disease", "Unknown") for r in records)
        top_disease, top_count = disease_counts.most_common(1)[0]
        hotspots.append(
            {
                "location": location,
                "lat": lat,
                "lon": lon,
                "scan_count": len(records),
                "top_disease": top_disease,
                "top_disease_count": top_count,
            }
        )
        if lat is not None and lon is not None:
            key = (round(lat, 1), round(lon, 1))
            cluster_counter[key] += len(records)

    hotspots.sort(key=lambda x: x["scan_count"], reverse=True)

    clusters = [
        {"grid_lat": k[0], "grid_lon": k[1], "scan_count": v}
        for k, v in sorted(cluster_counter.items(), key=lambda x: x[1], reverse=True)
    ]

    now_utc = datetime.utcnow()
    recent_window_start = now_utc - timedelta(days=7)
    previous_window_start = now_utc - timedelta(days=14)

    district_trends = []
    for location, records in by_location.items():
        disease_counts = Counter(r.get("disease", "Unknown") for r in records)
        top_disease = disease_counts.most_common(1)[0][0]

        recent_count = 0
        previous_count = 0
        for r in records:
            dt = _safe_date(r.get("date"))
            if not dt:
                continue
            if dt >= recent_window_start:
                recent_count += 1
            elif previous_window_start <= dt < recent_window_start:
                previous_count += 1

        trend_delta = recent_count - previous_count
        if trend_delta > 0:
            trend_direction = "up"
        elif trend_delta < 0:
            trend_direction = "down"
        else:
            trend_direction = "stable"

        district_trends.append(
            {
                "location": location,
                "scan_count": len(records),
                "top_disease": top_disease,
                "recent_count": recent_count,
                "previous_count": previous_count,
                "trend_delta": trend_delta,
                "trend_direction": trend_direction,
            }
        )

    district_trends.sort(
        key=lambda x: (x["trend_delta"], x["scan_count"]),
        reverse=True,
    )

    return {
        "total_scans": len(rows),
        "hotspots": hotspots[:50],
        "clusters": clusters[:30],
        "district_trends": district_trends[:30],
        "top_diseases": [{"disease": d, "count": c} for d, c in disease_counter.most_common(10)],
        "weekly_trend": [{"week": w, "count": c} for w, c in sorted(by_week.items())[-12:]],
    }
