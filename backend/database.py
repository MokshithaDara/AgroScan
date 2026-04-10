from pymongo import MongoClient

MONGO_URL = "mongodb+srv://agroscan@cluster0.0dtqxqy.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URL)

db = client["agroscan_db"]

scans_collection = db["scans"]