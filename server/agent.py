import anthropic
import time
from camera import Camera
from tools import tools
from drive import DriveToolExecutor

# Performs well with tools
ANTHROPIC_MODEL = "claude-sonnet-4-5-20250929"

class ClaudeAgent:
    def __init__(self):
        self.camera = Camera()
        self.executor = DriveToolExecutor()
        self.client = anthropic.Anthropic()
        self.model = ANTHROPIC_MODEL
        self.tools = tools

    def _process_tool_call(self, tool_name, tool_input):
        if tool_name == "drive_robot":
            return self.executor.execute(tool_input["direction"], tool_input["angle"])
            
    def run_until_finish(self, goal):
        """Run until finish with dashboard updates"""
        import asyncio
        from dashboard_server import send_photo, send_observation, send_command, send_agent_status
        
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": goal}
            ]
        }]

        print("Starting... \n")
        asyncio.run(send_agent_status(running=True))
        objective_complete = False
        MAX_HISTORY = 5
        try:
            while not objective_complete:
                image = self.camera.take_picture()
                
                asyncio.run(send_photo(image))

                messages.append({
                    "role": "user", 
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image
                            }
                        },
                        {"type": "text", "text": 
"New frame. One brief sentence describing what you see and your planned action. "
"Check your last 2-3 actions from message history to check for repetitive patterns. "
"If you notice you're alternating directions (e.g., 45°, -45°, 45°), break the pattern by choosing a different strategy. "
"Finally, call drive_robot with your next move."},
                    ]
                })
                
                print("Sending photo to Claude\n")

                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=600,
                    tools=self.tools,
                    messages=messages,
                )

                final_response = next(
                    (block.text for block in message.content if hasattr(block, "text")),
                    None,
                )

                print(f"\nFinal response: {final_response}")
                
                asyncio.run(send_observation(final_response))

                if message.stop_reason == "tool_use":
                    tool_use = next(block for block in message.content if block.type == "tool_use")
                    tool_name = tool_use.name
                    tool_input = tool_use.input

                    print(f"Claude is using tool: {tool_name}")
                    print(f"Direction = {tool_input['direction']}, angle = {tool_input['angle']}")
                    
                    asyncio.run(send_command(tool_input['direction'], tool_input['angle']))

                    if tool_input["direction"] == "x":
                        print("Claude indicated FINISH — stopping mission.")
                        objective_complete = True
                        break

                    tool_result = self._process_tool_call(tool_name, tool_input)
                    
                    messages.append({
                        "role": "assistant",
                        "content": final_response
                    })
                    
                    # Only keep the current image to maintain token usage
                    for i in range(len(messages) - 2, -1, -1):
                        if messages[i]["role"] == "user":
                            has_image = any(
                                isinstance(c, dict) and c.get("type") == "image" 
                                for c in messages[i]["content"]
                            )
                            if has_image:
                                messages.pop(i)
                                break

                    # Only keep the last MAX_HISTORY assistant messages
                    assistant_messages = [i for i, msg in enumerate(messages) if msg["role"] == "assistant"]
                    if len(assistant_messages) > MAX_HISTORY:
                        to_remove = assistant_messages[:-MAX_HISTORY]
                        for idx in reversed(to_remove):
                            messages.pop(idx)
                    
                    time.sleep(2)

        finally:
            asyncio.run(send_agent_status(running=False))
        
        return
