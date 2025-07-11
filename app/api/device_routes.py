from typing import Union
from fastapi import APIRouter, status
from app.driver.driver_factory import driver_factory

router = APIRouter()

# TODO: POST
@router.get("/register")
def read_register_device():
	from app.devices.device_manager import register_device
	try:
		# TODO: Dev example
		device = register_device(device_host="192.168.51.191", device_type="machine", device_driver="shelly_http")
		return {"message": "success", "device": device}
	except Exception as e:
		return {"message": "Error registering device", "error": str(e)} 
		# status.HTTP_400_BAD_REQUEST

@router.get("/list")
def request_get_devices():
	from app.devices.device_manager import get_devices
	devices = get_devices()
	return {"message": "success", "data": devices}

@router.get("/state")
def request_get_devices( id: Union[int, None] = None):

	if id is None:
		return {"message": "Missing device id specified"}
	
	from app.devices.device_manager import get_device

	device = get_device(id=id)

	if not device:
		return {"message": "Device not found"}

	driver = driver_factory(driver_type=device.device_driver, ip=device.device_host, relay=0, name=device.name)
	device = driver.get_state()
	return {"message": "success", "data": device}

@router.get("/event")
def event_device(on: Union[bool, None] = None, id: Union[int, None] = None):
	if on is None or id is None:
		return {"message": "No action specified"}
	
	from app.devices.device_manager import get_device
	
	device = get_device(id=id)

	if not device:
		return {"message": "Device not found"}

	driver = driver_factory(driver_type=device.device_driver, ip=device.device_host, relay=0, name=device.name)

	if on is True:
		driver.turn_on()
		return {"message": "einschalten", "state": driver.state}
	
	if on is False:
		driver.turn_off()
		return {"message": "ausschalten", "state": driver.state}
