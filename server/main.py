import asyncio
from agent import ClaudeAgent
from bridge import find_ble_device, websocket_listener
from bleak import BleakClient
from dashboard_server import (
    start_dashboard_server, set_connect_callback, set_disconnect_callback, set_mission_callback,
    send_status, send_goal, send_mission_status, send_ble_status,send_agent_status
)

agent = None
client_ref = None
ws_task = None



async def connect_to_robot():
    """Connect to BLE robot"""
    global agent, client_ref, ws_task
    
    print("Searching for robot...")
    await send_ble_status(connected=False)
    
    # Find BLE device
    device = await find_ble_device()
    if not device:
        print("Robot not found!")
        await send_ble_status(connected=False)
        return
    
    print(f"Connecting to {device.name}...")
    
    try:
        client_ref = BleakClient(device.address, timeout=20.0)
        await client_ref.connect()
        
        print(f"Connected to {device.name}!")
        await send_ble_status(connected=True)
        
        # Start WebSocket→BLE bridge
        ws_task = asyncio.create_task(websocket_listener(client_ref))
        await asyncio.sleep(2)
        
        # Initialize agent
        agent = ClaudeAgent()
        
        print("Robot ready for missions!")
        
    except Exception as e:
        print(f"Connection failed: {e}")
        await send_ble_status(connected=False)

async def disconnect_from_robot():
    """Disconnect from BLE robot"""
    global client_ref, ws_task
    
    print("Disconnecting from robot...")
    
    # Cancel WebSocket task
    if ws_task:
        ws_task.cancel()
        ws_task = None
    
    # Disconnect BLE
    if client_ref and client_ref.is_connected:
        await client_ref.disconnect()
    
    client_ref = None
    
    await send_ble_status(connected=False)
    await send_mission_status(running=False, complete=False)
    print("Disconnected!")

async def run_mission(goal):
    """Start the mission with the given goal"""
    if not client_ref or not client_ref.is_connected:
        print("Robot not connected!")
        await send_ble_status(connected=False)
        return
    
    print(f"Starting mission: {goal}")
    await send_goal(goal)
    await send_agent_status(running=True)
    await send_mission_status(running=True, complete=False)
    
    # Run agent in thread
    await asyncio.to_thread(agent.run_until_finish, goal)
    
    # Mission complete
    await send_mission_status(running=False, complete=True)
    await send_agent_status(running=False)
    print("Mission complete!")

async def main():
    # Start dashboard server
    dashboard_task = asyncio.create_task(start_dashboard_server())
    
    # Set callbacks
    set_connect_callback(connect_to_robot)
    set_disconnect_callback(disconnect_from_robot)
    set_mission_callback(run_mission)
    
    print("Dashboard server started!")
    print("Open dashboard.html in your browser at: file:///path/to/dashboard.html")
    print("Waiting for commands from dashboard...")
    
    # Keep running
    await dashboard_task

if __name__ == "__main__":
    asyncio.run(main())
