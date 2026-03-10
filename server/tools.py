VALID_ANGLES = [0, 15, 45, 90, 135, 180,-15, -45, -90, -135]
VALID_DIRECTIONS = ["f", "b", "s", "x"]

tools = [{
    "name": "drive_robot",
    "description": (
        "Drive the robot one step. Use direction ∈ {f, b, s, x} where:"
        "- 'f' = forward (move ahead)"
        "- 'b' = backward (reverse)"
        "- 's' = stationary (turn in place, no forward/backward movement)"
        "- 'x' = task complete (stop)"
        "Angle options (degrees): 0, 15, 45, 90, 135, 180, -15, -45, -90, -135."
        "- Positive angles = clockwise turn"
        "- Negative angles = counter-clockwise turn"
        ""
        "Movement behavior: Robot turns FIRST, then moves in the specified direction for 1 second."
        "You are using iPhone 14 Pro Camera with 120° Field of View (FOV)"
        ""
        "Strategy guidelines:"
        "1. If low visibility or facing a wall, move backward (b, 0) to get distance"
        "2. Start by surveying: use stationary turns (s) to scan 360° in small increments (15°)"
        "3. Once target spotted, approach with small adjustments (15° turns)"
        "4. CRITICAL: Check your last 3 moves in message history before deciding:"
        "   - If alternating between opposite angles (45°, -45°, 45°), you're stuck - break out by moving forward/backward"
        "   - If you've turned 180°+ without finding target, try moving to a new position"
        "   - If you've done 3+ stationary rotations, switch to forward/backward movement"
        "5. When navigating toward target, prefer forward movement with small angle adjustments"
        "6. Navigation rule: Coarse scanning (45-90°) → Target spotted → Fine adjustment (15°) → Approach (forward with 15° tweaks)"
        "7. Call direction='x', angle=0 ONLY when task is definitively complete"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "direction": {
                "type": "string",
                "enum": VALID_DIRECTIONS,
                "description": "The direction the robot will move in for 1 seconds. f is forward. b is backward. s is stationary. and x is for when you think the task is complete.."
            },
            "angle": {
                "type": "integer",
                "enum": VALID_ANGLES,
                "description": "Clockwise turn before moving in degrees. Use 0 for no turn or when finish."
            }
        },
        "required": ["direction", "angle"]
    }
}]
