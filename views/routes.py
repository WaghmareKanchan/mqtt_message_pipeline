# ═══════════════════════════════════════════════════
#  views/routes.py
#  VIEW — Flask API routes
#  Only handles HTTP request/response
#  Calls Controller for all business logic
# ═══════════════════════════════════════════════════

from flask import Blueprint, jsonify, request

# Blueprint groups all routes
message_bp = Blueprint("messages", __name__)

# controller injected from app.py
controller = None

def init_routes(ctrl):
    """Inject controller into routes"""
    global controller
    controller = ctrl

# ── GET /  ──────────────────────────────────────────
@message_bp.route("/", methods=["GET"])
def home():
    return jsonify({
        "status"  : " Flask MVC running",
        "flow"    : "Tkinter → MQTT → POST /messages → MongoDB",
        "database": "mqtt_api_db",
        "routes"  : {
            "POST   /messages"      : "auto-called by MQTT",
            "GET    /messages"      : "get all messages",
            "GET    /messages/<id>" : "get one message",
            "GET    /messages/count": "total count",
            "DELETE /messages/<id>" : "delete one",
            "DELETE /messages/all"  : "delete all"
        }
    }), 200

# ── POST /messages ───────────────────────────────────
#  Called AUTOMATICALLY by MQTTController via HTTP
#  Never call this manually
# ────────────────────────────────────────────────────
@message_bp.route("/messages", methods=["POST"])
def save():
    body         = request.get_json()
    data, status = controller.save(body)
    return jsonify(data), status

# ── GET /messages ─────────────────────────────────────
@message_bp.route("/messages", methods=["GET"])
def get_all():
    data, status = controller.get_all()
    return jsonify(data), status

# ── GET /messages/count ───────────────────────────────
@message_bp.route("/messages/count", methods=["GET"])
def get_count():
    data, status = controller.get_count()
    return jsonify(data), status

# ── GET /messages/<id> ────────────────────────────────
@message_bp.route("/messages/<id>", methods=["GET"])
def get_one(id):
    data, status = controller.get_one(id)
    return jsonify(data), status

# ── DELETE /messages/all ──────────────────────────────
@message_bp.route("/messages/all", methods=["DELETE"])
def delete_all():
    data, status = controller.delete_all()
    return jsonify(data), status

# ── DELETE /messages/<id> ─────────────────────────────
@message_bp.route("/messages/<id>", methods=["DELETE"])
def delete_one(id):
    data, status = controller.delete_one(id)
    return jsonify(data), status