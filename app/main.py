from typing import Union
from fastapi import FastAPI, status 
from app.db.session import initialize_database
from app.api import device_routes
from app.core.scheduler import start_scheduler

initialize_database()
app = FastAPI()
app.include_router(device_routes.router, prefix="/api/device", tags=["Devices"])


@app.get("/")
def read_root():
	return {"message": "Welcome	to IoT Space!"}


@app.get("/health")
def read_healt():
	# do something with a device
	return {"message": "fine"}


# TODO: In threads unterteilen, z.B. device auth etc.
start_scheduler()