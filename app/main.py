from typing import Union
from fastapi import FastAPI, status 
from app.db.session import initialize_database
from app.api import device_routes
from app.api import auth_routes
from app.api import config_routes
from app.core.scheduler import start_scheduler
from app.driver.default_nfc_reader import NfcReader
from app.driver.default_data_scanner import DefaultDataScanner
from app.driver.driver_factory import driver_factory
from app.core.health import HealthCheck
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select
from app.db.models import Device
import logging

import os
import sys

logger = logging.getLogger("uvicorn.error")


def get_db_path(filename="data.db"):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(os.path.dirname(sys.executable), filename)
    else:
        return os.path.abspath(filename)

db_path = get_db_path()

# Async Engine für FastAPI-Lifespan
DATABASE_ASYNC_URL = f"sqlite+aiosqlite:///{db_path}"
async_engine = create_async_engine(DATABASE_ASYNC_URL, echo=False)

async_session_maker = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

def get_async_session() -> AsyncSession:
    return async_session_maker()

initialize_database()

@asynccontextmanager
async def lifespan(app: FastAPI):
	start_scheduler()

	# TODO: Refactor implment connection class etc.
	async with get_async_session() as session:
		try:
			from app.devices.device_manager import get_devices_serial
			devices = get_devices_serial()
			
			logger.info(f"Found {len(devices)} serial devices configs from DB")
			for device in devices:
				try:
					logger.info(f"==> factory driver: {device['name']} ({device['device_type']}) on {device['device_host']} with driver {device['device_driver_name']}")
					driver = driver_factory(driver_type=device["device_driver_name"], args={'port': device["device_host"], 'baudrate': device["baudrate"]})
					driver.listen_in_thread()
				except Exception as e:
					logger.error(str(e))
		except Exception as e:
			logger.error(str(e))
			pass
	yield


app = FastAPI(lifespan=lifespan)
app.include_router(config_routes.router, prefix="/api/config", tags=["Config"])
app.include_router(device_routes.router, prefix="/api/device", tags=["Devices"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])


@app.get("/")
def read_root():
	return {"message": "Welcome	to IoT Space!"}


@app.get("/health")
def read_healt():
	# do something with a device
	return {"message": "fine"}


logger.info("IoT Space is running! 0.2.3")
logger.info(HealthCheck("IoT Space", "OK").getThreads())