import os
import logging

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import PyMongoError

load_dotenv()
logger = logging.getLogger("agroscan.database")

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "agroscan_db")

client = None
db = None
scans_collection = None

if not MONGO_URL:
    logger.warning(
        "MONGO_URL is not set. Running without database; history APIs will be unavailable."
    )
else:
    try:
        client = MongoClient(
            MONGO_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
        )
        db = client[MONGO_DB_NAME]
        scans_collection = db["scans"]
        scans_collection.create_index([("user_id", ASCENDING), ("date", DESCENDING)])
    except PyMongoError as e:
        logger.error(
            "MongoDB connection failed. Running without database support: %s",
            e,
        )
        scans_collection = None
