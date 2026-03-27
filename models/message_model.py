from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import sys

class MessageModel:

    def __init__(self):
        print("\n [MODEL] Connecting to MongoDB...")
        try:
            self.mongo = MongoClient(
                "mongodb://localhost:27017/",
                serverSelectionTimeoutMS=4000
            )
            self.mongo.server_info()
            self.db  = self.mongo["mqtt_api_db"]
            self.col = self.db["messages"]
            print(" [MODEL] MongoDB connected!")
            print("   DB  → mqtt_api_db")
            print("   Col → messages\n")
        except Exception as e:
            print(f" [MODEL] MongoDB NOT running!")
            print(f"   Error : {e}")
            print(f"   FIX   → run: mongod\n")
            sys.exit(1)

    # ── fix ObjectId → string ────────────────────
    def _fix_id(self, doc):
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def _fix_ids(self, docs):
        return [self._fix_id(d) for d in docs]

    # ── INSERT one document ──────────────────────
    def insert(self, data: dict) -> dict:
        """Saves one document to MongoDB"""
        data["saved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result      = self.col.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return data

    # ── FIND all documents ───────────────────────
    def find_all(self) -> list:
        """Returns all documents"""
        return self._fix_ids(list(self.col.find()))

    # ── FIND one by id ───────────────────────────
    def find_by_id(self, id: str) -> dict:
        """Returns one document by _id"""
        try:
            doc = self.col.find_one({"_id": ObjectId(id)})
            return self._fix_id(doc)
        except Exception:
            return None

    # ── COUNT documents ──────────────────────────
    def count(self) -> int:
        """Returns total document count"""
        return self.col.count_documents({})

    # ── DELETE one by id ─────────────────────────
    def delete_by_id(self, id: str) -> bool:
        """Deletes one document by _id"""
        try:
            result = self.col.delete_one({"_id": ObjectId(id)})
            return result.deleted_count > 0
        except Exception:
            return False

    # ── DELETE all documents ─────────────────────
    def delete_all(self) -> int:
        """Deletes all documents, returns count"""
        return self.col.delete_many({}).deleted_count