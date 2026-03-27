import paho.mqtt.client as mqtt
import time, threading

class MQTTController:

    def __init__(self, broker, port, topic, message_controller):
        self.broker             = broker
        self.port               = port
        self.topic              = topic
        self.message_controller = message_controller  # injected
        self.client             = None

    def start(self):
        """Connect to MQTT broker and start listening"""
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION1,
            client_id=f"flask-{int(time.time())}",
            clean_session=True
        )
        self.client.on_connect    = self._on_connect
        self.client.on_message    = self._on_message
        self.client.on_disconnect = self._on_disconnect

        print(f" [MQTT CONTROLLER] Connecting → {self.broker}:{self.port}")
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()   # background thread
        except Exception as e:
            print(f" [MQTT CONTROLLER] Failed: {e}")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.subscribe(self.topic, qos=1)
            print(f" [MQTT CONTROLLER] Connected!")
            print(f"   Broker → {self.broker}:{self.port}")
            print(f"   Topic  → {self.topic}")
            print(f" Waiting for Tkinter messages...\n")
        else:
            print(f" [MQTT CONTROLLER] Failed (rc={rc})")

    def _on_message(self, client, userdata, msg):
        """
        Fires automatically when Tkinter publishes.
        Passes raw message to MessageController.
        Uses thread to avoid blocking MQTT loop.
        """
        raw   = msg.payload.decode("utf-8")
        topic = msg.topic
        print(f"\n [MQTT CONTROLLER] Message received!")
        print(f"   topic   : {topic}")
        print(f"   payload : {raw}")

        # pass to controller in background thread
        threading.Thread(
            target=self.message_controller.handle_mqtt_message,
            args=(topic, raw),
            daemon=True
        ).start()

    def _on_disconnect(self, client, userdata, rc):
        print(f"\n [MQTT CONTROLLER] Disconnected (rc={rc})")