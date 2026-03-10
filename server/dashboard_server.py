import asyncio
import websockets
import json
import traceback
import time

connected_clients = set()
mission_goal = None
connect_callback = None
disconnect_callback = None
mission_callback = None

current_ble_status = False
current_agent_status = False

async def broadcast(message):
    """Send message to all connected dashboard clients"""
    if not connected_clients:
        return
    
    disconnected = set()
    for client in connected_clients:
        try:
            await client.send(json.dumps(message))
        except:
            disconnected.add(client)
    
    # Remove disconnected clients
    connected_clients.difference_update(disconnected)

async def dashboard_handler(websocket):
    """Handle dashboard WebSocket connections"""
    connected_clients.add(websocket)
    print(f"Dashboard client connected. Total clients: {len(connected_clients)}")
    
    try:
        # Send initial status
        await websocket.send(json.dumps({
            'type': 'status',
            'ble_connected': current_ble_status,
            'agent_running': current_agent_status
        }))
        
        # Listen for messages from dashboard
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"Received from dashboard: {data['type']}")
                
                if data['type'] == 'connect_robot' and connect_callback:
                    asyncio.create_task(connect_callback())
                    
                elif data['type'] == 'disconnect_robot' and disconnect_callback:
                    asyncio.create_task(disconnect_callback())
                    
                elif data['type'] == 'start_mission' and mission_callback:
                    global mission_goal
                    mission_goal = data['goal']
                    asyncio.create_task(mission_callback(data['goal']))
                    
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
            except Exception as e:
                print(f"Error processing message: {e}")
                traceback.print_exc()
                
    except websockets.exceptions.ConnectionClosed:
        print("Dashboard client disconnected (connection closed)")
    except Exception as e:
        print(f"Dashboard handler error: {e}")
        traceback.print_exc()
    finally:
        connected_clients.discard(websocket)
        print(f"Dashboard client removed. Total clients: {len(connected_clients)}")

async def start_dashboard_server():
    """Start WebSocket server for dashboard"""
    try:
        async with websockets.serve(dashboard_handler, 'localhost', 8765):
            print("Dashboard WebSocket server running on ws://localhost:8765")
            await asyncio.Future()  # run forever
    except Exception as e:
        print(f"Failed to start dashboard server: {e}")
        traceback.print_exc()

def set_connect_callback(callback):
    """Set the callback function to connect to robot"""
    global connect_callback
    connect_callback = callback

def set_disconnect_callback(callback):
    """Set the callback function to disconnect from robot"""
    global disconnect_callback
    disconnect_callback = callback

def set_mission_callback(callback):
    """Set the callback function to start missions"""
    global mission_callback
    mission_callback = callback


async def send_ble_status(connected):
    """Send only BLE connection status"""
    global current_ble_status
    current_ble_status = connected
    await broadcast({
        'type': 'ble_status',
        'connected': connected
    })

async def send_agent_status(running):
    """Send only agent running status"""
    global current_agent_status
    current_agent_status = running
    await broadcast({
        'type': 'agent_status',
        'running': running
    })
    
# Functions to call from your agent code
async def send_status(ble_connected, agent_running):
    global current_ble_status, current_agent_status
    current_ble_status = ble_connected
    current_agent_status = agent_running
    await broadcast({
        'type': 'status',
        'ble_connected': ble_connected,
        'agent_running': agent_running
    })

async def send_mission_status(running=False, complete=False):
    await broadcast({
        'type': 'mission_status',
        'running': running,
        'complete': complete
    })

async def send_goal(goal_text):
    await broadcast({
        'type': 'goal',
        'goal': goal_text
    })

async def send_observation(text):
    await broadcast({
        'type': 'observation',
        'text': text
    })

async def send_command(direction, angle):
    await broadcast({
        'type': 'command',
        'direction': direction,
        'angle': angle
    })

async def send_photo(base64_image):
    # Just notify dashboard that a new photo is available
    await broadcast({
        'type': 'photo_update',
        'timestamp': time.time()  # Force cache bust
    })