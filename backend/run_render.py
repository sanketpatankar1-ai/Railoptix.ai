import subprocess
import os

def start():
    print("Intercepted 'Railoptix.ai' command. Starting FastAPI server...")
    port = os.getenv("PORT", "8000")
    subprocess.run(["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", port])

if __name__ == "__main__":
    start()
