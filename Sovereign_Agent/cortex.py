
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import sys

# Add root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="Cortex: Sovereign Local Agent")

class CommandRequest(BaseModel):
    action: str
    parameters: dict = {}

@app.get("/")
def health_check():
    return {"status": "online", "system": "Cortex V1"}

@app.post("/execute")
def execute_command(cmd: CommandRequest):
    """
    Executes a local command via the Input Module.
    """
    print(f"⚡ [CORTEX] Received Command: {cmd.action}")
    
    if cmd.action == "mouse_move":
        # Deferred import to prevent crash in headless mode if not needed
        try:
            from effectors.input_module import InputModule
            InputModule.move_mouse(cmd.parameters.get("x", 0), cmd.parameters.get("y", 0))
            return {"status": "success", "action": "mouse_move"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    elif cmd.action == "open_browser":
        import webbrowser
        url = cmd.parameters.get("url", "https://google.com")
        webbrowser.open(url)
        return {"status": "success", "opened": url}

    elif cmd.action == "screenshot":
        # Deferred import
        try:
            from effectors.input_module import InputModule
            filename = cmd.parameters.get("filename", "screenshot.png")
            path = InputModule.take_screenshot(filename)
            return {"status": "success", "file": path}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    else:
        return {"status": "unknown_command", "command": cmd.action}

if __name__ == "__main__":
    import uvicorn
    print("🧠 Cortex Server Starting on Port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
