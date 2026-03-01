from fastapi import FastAPI 
import tomllib
from app.api import device_routes
from app.api import auth_routes
from app.api import config_routes
from app.db.session import initialize_database
from app.core.utils import get_resource_path
from app.core.threadrunner import start_threading
from app.core.scheduler import start_scheduler
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger("uvicorn.error")
initialize_database()

@asynccontextmanager
async def lifespan(app: FastAPI):
	start_scheduler()
	await start_threading()
	yield

app = FastAPI(lifespan=lifespan)
app.include_router(config_routes.router, prefix="/api/config", tags=["Config"])
app.include_router(device_routes.router, prefix="/api/device", tags=["Devices"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])


@app.get("/")
def read_root():
	return {"message": "Welcome	to IoT Hub!"}


@app.get("/health")
def read_healt():
	# do something with a device
	return {"message": "fine"}


TOML_PATH = get_resource_path("pyproject.toml")
with open(TOML_PATH, "rb") as f:
	config = tomllib.load(f)

# TODO: Output system information here
logger.info("%s %s is running", config["project"]["name"], config["project"]["version"]) 