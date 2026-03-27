# ═══════════════════════════════════════════════════
#  controllers/message_controller.py
#  CONTROLLER — business logic
#  Sits between MQTT/Routes and the Model
#  Processes data before saving or returning it
# ═══════════════════════════════════════════════════

import json
import requests as http
from datetime import datetime

OWN_API = "http://localhost:5000/messages"   # Flask calls itself dynamically

class MessageController:

    def __init__(self, model):
        self.model = model    # injected from app.py

    # ── Called by MQTT Controller ────────────────
    def handle_mqtt_message(self, topic: str, raw: str):
        """
        CONTROLLER processes the raw MQTT message:
        1. Parse JSON dynamically
        2. Add mqtt_topic field
        3. Call OWN API dynamically via HTTP POST
        """
        print(f"\n [CONTROLLER] Processing message...")
        print(f"   topic   : {topic}")
        print(f"   raw     : {raw}")

        # step 1 — parse JSON dynamically
        try:
            data = json.loads(raw)
            print(f" [CONTROLLER] JSON parsed: {data}")
        except Exception:
            data = {"raw_message": raw}
            print(f"  [CONTROLLER] Plain text wrapped")

        # step 2 — add topic dynamically
        data["mqtt_topic"] = topic

        # step 3 — call OWN API dynamically (not hardcoded save)
        print(f" [CONTROLLER] Calling POST {OWN_API} dynamically...")
        try:
            response = http.post(
                OWN_API,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            result = response.json()
            if result.get("success"):
                print(f" [CONTROLLER] API called → saved to MongoDB!")
                print(f"   _id  : {result['data']['_id']}")
                print(f"   name : {result['data'].get('name', 'N/A')}")
                print(f"   msg  : {result['data'].get('msg',  'N/A')}")
            else:
                print(f" [CONTROLLER] API error: {result.get('error')}")
        except Exception as e:
            print(f" [CONTROLLER] API call failed: {e}")

    # ── Called by Flask Routes (VIEW) ────────────
    def save(self, body: dict):
        """
        Validates and saves data via MODEL.
        Called by POST /messages route.
        """
        if not body:
            return {"success": False, "error": "Empty body"}, 400

        # save dynamically — whatever fields came in
        saved = self.model.insert(body)
        print(f" [CONTROLLER] Saved via model: {saved}")
        return {"success": True,
                "message": "Saved to MongoDB",
                "data"   : saved}, 201

    def get_all(self):
        """Returns all messages via MODEL"""
        docs = self.model.find_all()
        return {"success": True,
                "total"  : len(docs),
                "messages": docs}, 200

    def get_one(self, id: str):
        """Returns one message by id via MODEL"""
        doc = self.model.find_by_id(id)
        if not doc:
            return {"success": False,
                    "error": f"No message: {id}"}, 404
        return {"success": True, "message": doc}, 200

    def get_count(self):
        """Returns total count via MODEL"""
        return {"success": True,
                "count": self.model.count()}, 200

    def delete_one(self, id: str):
        """Deletes one message via MODEL"""
        deleted = self.model.delete_by_id(id)
        if not deleted:
            return {"success": False,
                    "error": f"No message: {id}"}, 404
        return {"success": True, "message": "Deleted"}, 200

    def delete_all(self):
        """Deletes all messages via MODEL"""
        n = self.model.delete_all()
        return {"success": True, "deleted": n}, 200