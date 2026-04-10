from datetime import datetime
from database import scans_collection


def save_scan(user_id, location, disease):
    
    record = {
        "user_id": user_id,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "location": location,
        "disease": disease
    }

    scans_collection.insert_one(record)


def get_history(user_id):

    data = list(
        scans_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("date", -1)
    )

    return data