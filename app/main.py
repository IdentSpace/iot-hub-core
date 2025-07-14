from typing import Union
from fastapi import FastAPI, status 
from app.db.session import initialize_database
from app.api import device_routes
from app.api import auth_routes
from app.core.scheduler import start_scheduler
from app.devices.nfc_reader import NfcReader
from app.core.health import HealthCheck
from contextlib import asynccontextmanager

initialize_database()

@asynccontextmanager
async def lifespan(app: FastAPI):
	start_scheduler()
	reader_thread = NfcReader().listen_in_thread()
	yield


app = FastAPI(lifespan=lifespan)
app.include_router(device_routes.router, prefix="/api/device", tags=["Devices"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])


@app.get("/")
def read_root():
	return {"message": "Welcome	to IoT Space!"}


@app.get("/health")
def read_healt():
	# do something with a device
	return {"message": "fine"}


print("IoT Space is running!")
print(HealthCheck("IoT Space", "OK").getThreads())