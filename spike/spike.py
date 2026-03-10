from BLE_CEEO import Yell
import json

from hub import light_matrix, port, sound
import runloop
import time
import motor_pair

async def turn(angle):
    absolute_angle = abs(angle)
    angle_map = {0: 0, 15: 30, 45: 85, 90: 170, 135: 215, 180: 340}
    if absolute_angle in angle_map:
        degrees = angle_map[absolute_angle]
        if angle > 0:
            await motor_pair.move_tank_for_degrees(motor_pair.PAIR_1, degrees, 1000, -1000) # clockwise tank
        else:
            await motor_pair.move_tank_for_degrees(motor_pair.PAIR_1, degrees, -1000, 1000) # anticlockwise tank

async def drive(direction):
    if direction == "f":
        await motor_pair.move_for_time(motor_pair.PAIR_1, 1000, 0, velocity=-1000)
    elif direction == "b":
        await motor_pair.move_for_time(motor_pair.PAIR_1, 1000, 0, velocity=1000)

async def play_connection_tune():
    await sound.beep(523, 200, 100)
    await sound.beep(659, 200, 100)
    await sound.beep(784, 400, 100)

async def play_command_beep():
    await sound.beep(800, 100, 80)

def callback(data):
    try:
        decoded = data.decode()
        parsed = json.loads(decoded)
        direction = parsed.get('d')
        angle = parsed.get('a')
        print(f"Direction: {direction}, Angle: {angle}")

        runloop.run(play_command_beep())
        runloop.run(turn(angle))
        runloop.run(drive(direction))
    except Exception as e:
        print(e)

def peripheral(): 
    while True:  # Infinite loop for auto-reconnect
        light_matrix.clear()  # Clear when disconnected
        print("Attempting to connect...")
        
        p = Yell("Spike", interval_us=3000, verbose=True)
        if p.connect_up():
            print("Connected")
            light_matrix.show_image(light_matrix.IMAGE_HAPPY)  # Show happy face when connected
            
            runloop.run(play_connection_tune())
            p.callback = callback
            
            while p.is_connected:
                time.sleep(0.1)
            
            print("Connection lost, retrying...")
            light_matrix.clear()
        else:
            print("Connection failed, retrying in 2 seconds...")
            time.sleep(2)

async def main():
    motor_pair.unpair(motor_pair.PAIR_1)
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.B)
    peripheral()

runloop.run(main())