# ═══════════════════════════════════════════════════
#  Terminal 1 → python app.py
#  Terminal 2 → python tkinter_app.py
#
#  Check data:
#  GET http://localhost:5000/messages
# ═══════════════════════════════════════════════════

from flask import Flask

# ── MVC imports ──────────────────────────────────
from models.message_model           import MessageModel
from controllers.message_controller import MessageController
from controllers.mqtt_controller    import MQTTController
from views.routes                   import message_bp, init_routes

# ── MQTT settings ────────────────────────────────
BROKER = "broker.emqx.io"
PORT   = 1883
TOPIC  = "test/tkinter"

# ════════════════════════════════════════════════
#  WIRE MVC TOGETHER
#
#  MODEL      → MessageModel       (database layer)
#  CONTROLLER → MessageController  (business logic)
#  VIEW       → routes.py          (HTTP routes)
#  MQTT       → MQTTController     (MQTT subscriber)
# ════════════════════════════════════════════════

# Create MODEL
model = MessageModel()

# Create CONTROLLER — inject model
controller = MessageController(model)

# Create MQTT CONTROLLER — inject message controller
mqtt_ctrl = MQTTController(BROKER, PORT, TOPIC, controller)
mqtt_ctrl.start()   # connects and starts listening

app = Flask(__name__)

# Init VIEW (routes) — inject controller
init_routes(controller)

# Register Blueprint
app.register_blueprint(message_bp)


if __name__ == "__main__":
    print("\n Flask MVC server started!")
    print("   URL     → http://localhost:5000")
    print("   GET all → http://localhost:5000/messages\n")
    app.run(host="0.0.0.0", port=5000,
            debug=False, use_reloader=False)