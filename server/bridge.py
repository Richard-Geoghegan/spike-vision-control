import asyncio
from bleak import BleakClient, BleakScanner
import websockets
import json

UART_RX_CHAR_UUID = "0000fd02-0001-1000-8000-00805f9b34fb"

USER = "chrisrogers"
PROJECT = "talking-on-a-channel"
CHANNEL = "hackathon"
WS_URL = f"wss://{USER}.pyscriptapps.com/{PROJECT}/api/channels/{CHANNEL}"
WS_PING_SECS = 20
WS_RETRY_SECS = 5

async def find_ble_device():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover(timeout=60.0)
    
    for device in devices:
        print(f"Found: {device.name} - {device.address}")
        if device.name == "jj":
            return device
    
    return None

async def websocket_listener(client):
    while True:
        try:
            print(f"[WS] Connecting to {WS_URL}")
            async with websockets.connect(WS_URL, ping_interval=WS_PING_SECS) as ws:
                print(f"[WS] CONNECTED Listening...")

                async for raw in ws:
                    try:
                        msg = json.loads(raw)
                    except:
                        print(f"[WARN] WS not JSON: {raw}")
                        continue

                    if msg.get("type") != "data" or "payload" not in msg:
                        continue

                    try:
                        payload = json.loads(msg["payload"])
                        print(f"[WS] Received: {payload}")
                    except:
                        print(f"[ERROR] payload not JSON")
                        continue

                    topic = payload.get("topic", "")
                    value = payload.get("value", "")

                    if topic != "robot_command":
                        continue

                    if not isinstance(value, str):
                        value = json.dumps(value)

                    print(f"[FORWARD] Sending to SPIKE: {value}")
                    
                    # Send to SPIKE via BLE
                    data = value.encode('utf-8')
                    await client.write_gatt_char(UART_RX_CHAR_UUID, data)
                    print(f"[BLE] Sent")

        except Exception as e:
            print(f"[WS-ERROR] {e}  RETRYING...")
            await asyncio.sleep(WS_RETRY_SECS)
