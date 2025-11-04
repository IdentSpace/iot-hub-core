import os
import sys
from dotenv import load_dotenv
import uvicorn
import serial
from typing import Union
from fastapi import FastAPI, status 
from app.db.session import initialize_database
from app.api import device_routes
from app.api import auth_routes
from app.core.scheduler import start_scheduler
from app.driver.default_nfc_reader import NfcReader
from app.driver.default_data_scanner import DefaultDataScanner
from app.core.health import HealthCheck
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select
from app.db.models import Device
from sqlmodel import select


# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main():
    load_dotenv()
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)  # reload=False!
    
if __name__ == "__main__":
    main()
    input("Press Enter to exit...")