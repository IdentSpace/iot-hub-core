from app.driver.driver_factory import driver_factory
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
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

DATABASE_ASYNC_URL = f"sqlite+aiosqlite:///{db_path}"
async_engine = create_async_engine(DATABASE_ASYNC_URL, echo=False)

async_session_maker = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

def get_async_session() -> AsyncSession:
    return async_session_maker()



running_driver_threads = []

async def start_threading():
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
					running_driver_threads.append(driver)
				except Exception as e:
					logger.error(str(e))
		except Exception as e:
			logger.error(str(e))
			pass

def restart_threads():
	for driver in running_driver_threads:
		try:
			driver.close()
		except Exception as e:
			logger.error(f"Error stopping driver {driver.name}: {str(e)}")
	
	running_driver_threads.clear()
	start_threading()