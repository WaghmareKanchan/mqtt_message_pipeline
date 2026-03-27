from flask import Flask

from models.message_model           import MessageModel 
from controllers.message_controller import MessageController 
from controllers.mqtt_controller    import MQTTController 
from views.routes                   import message_bp, init_routes 

BROKER = "broker.emqx.io"
PORT   = 1883
TOPIC  = "test/tkinter"

model = MessageModel()

controller = MessageController(model)

mqtt_ctrl = MQTTController(BROKER, PORT, TOPIC, controller)
mqtt_ctrl.start()

app = Flask(__name__)

init_routes(controller)

app.register_blueprint(message_bp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)