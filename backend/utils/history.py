from datetime import datetime
from database import scans_collection
from utils.sqlite_history_store import append_scan, read_user_scans


def save_scan(
    user_id,
    location,
    disease,
    treatment="",
    treatment_steps=None,
    products_recommended=None,
):
    safe_treatment_steps = treatment_steps or []
    safe_products = products_recommended or []

    record = {
        "user_id": user_id,
        "date": datetime.utcnow(),
        "location": location,
        "disease": disease,
        "treatment": treatment or "",
        "treatment_steps": safe_treatment_steps,
        "products_recommended": safe_products,
    }

    if scans_collection is None:
        local_record = dict(record)
        local_record["date"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        append_scan(local_record)
        return

    scans_collection.insert_one(record)


def get_history(user_id, limit=10, skip=0):
    if scans_collection is None:
        rows = read_user_scans(user_id)
        sliced = rows[max(0, skip): max(0, skip) + limit]
        for row in sliced:
            if "treatment" not in row:
                row["treatment"] = ""
            if "treatment_steps" not in row or not isinstance(row.get("treatment_steps"), list):
                row["treatment_steps"] = []
            if "products_recommended" not in row or not isinstance(row.get("products_recommended"), list):
                row["products_recommended"] = []
        return sliced

    data = list(
        scans_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("date", -1).skip(max(0, skip)).limit(limit)
    )

    for row in data:
        value = row.get("date")
        if isinstance(value, datetime):
            row["date"] = value.strftime("%Y-%m-%d %H:%M:%S")
        if "treatment" not in row:
            row["treatment"] = ""
        if "treatment_steps" not in row or not isinstance(row.get("treatment_steps"), list):
            row["treatment_steps"] = []
        if "products_recommended" not in row or not isinstance(row.get("products_recommended"), list):
            row["products_recommended"] = []

    return data


def get_total_scans(user_id):
    if scans_collection is None:
        return len(read_user_scans(user_id))
    return scans_collection.count_documents({"user_id": user_id})
