import os
import subprocess
from dotenv import load_dotenv

def main():
    load_dotenv()

    os.environ["PYTHONPATH"] = "."
    venv_bin = "/opt/iot-hub-core/venv/bin"
    cmd = [
        # "uvicorn",
        os.path.join(venv_bin, "uvicorn"),
        "app.main:app",
        "--reload",
        "--host",
        # "127.0.0.1",
        "0.0.0.0",
        "--port",
        os.getenv("APP_PORT", "8000"),
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()