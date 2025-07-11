import os
import subprocess
from dotenv import load_dotenv

def main():
    load_dotenv()

    os.environ["PYTHONPATH"] = "."
    cmd = [
        "uvicorn",
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        os.getenv("APP_PORT", "8000"),
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()