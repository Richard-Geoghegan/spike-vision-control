import json
import websocket
from tools import VALID_ANGLES, VALID_DIRECTIONS

PYSCRIPT_CHANNEL = "hackathon"
PYSCRIPT_USER = "chrisrogers"
PYSCRIPT_PROJECT = "talking-on-a-channel"
PYSCRIPT_URL = f"wss://{PYSCRIPT_USER}.pyscriptapps.com/{PYSCRIPT_PROJECT}/api/channels/{PYSCRIPT_CHANNEL}"
PYSCRIPT_TOPIC = "robot_command"

class DriveToolExecutor:
    def __init__(self):
        self.ws_url = PYSCRIPT_URL
        self.topic = PYSCRIPT_TOPIC

    def _publish_to_pyscript(self, value):
        try:
            payload = {"topic": self.topic, "value": value}
        
            ws = websocket.create_connection(self.ws_url, timeout=10)
            ws.send(json.dumps(payload))
            ws.close()
        
            return f"Successfully published: value='{value}'"
        except Exception as e:
            return f"Failed to publish message: {str(e)}"
        
    def execute(self, direction, angle):
        if direction not in VALID_DIRECTIONS:
            raise ValueError(f"Direction must be one of {VALID_DIRECTIONS} (got {direction})")

        if angle not in VALID_ANGLES:
            raise ValueError(f"Angle must be one of {VALID_ANGLES} (got {angle})")
        
        if direction == "finish":
            angle = 0

        command = {
            "d": direction,
            "a": angle
        }

        publish_response = self._publish_to_pyscript(command)

        return f"Published: {command}, Response: {publish_response}"
