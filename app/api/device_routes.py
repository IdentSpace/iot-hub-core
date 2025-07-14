from typing import Union
from uuid import UUID
from fastapi import APIRouter, status
from app.driver.driver_factory import driver_factory
from app.api.response import IHCApiResponse

router = APIRouter()

# TODO: POST
@router.get("/register")
def read_register_device() :
	from app.devices.device_manager import register_device
	try:
		# TODO: Dev example
		device = register_device(device_host="192.168.51.191", device_type="machine", device_driver="shelly_http")
		return IHCApiResponse(message="success").add_data(key="device", value=device).to_dict()
	
	except Exception as e:
		return IHCApiResponse(message="error").add_error(key="device", value=str(e)).to_dict()
		# status.HTTP_400_BAD_REQUEST

@router.get("/list")
def request_get_devices() :
	from app.devices.device_manager import get_devices
	devices = get_devices()
	return IHCApiResponse(message="success").add_data(key="device", value=devices).to_dict()

@router.get("/{id}/state")
def request_get_devices_state(id: UUID) :

	if id is None:
		return IHCApiResponse(message="error").add_error(key="device", value="Missing device id specified").to_dict()
	
	from app.devices.device_manager import get_device
	device = get_device(id=id)

	if not device:
		return IHCApiResponse(message="error").add_error(key="device", value="Device not fount").to_dict()

	driver = driver_factory(driver_type=device.device_driver, ip=device.device_host, relay=0, name=device.name)
	device = driver.get_state()
	return IHCApiResponse(message="success").add_data(key="device", value=device).to_dict()

@router.get("/event")
def event_device(on: Union[bool, None] = None, id: Union[UUID, None] = None) :
	if on is None or id is None:
		return IHCApiResponse(message="error").add_error(key="device", value="Missing event or device id").to_dict()
	
	from app.devices.device_manager import get_device
	
	device = get_device(id=id)

	if not device:
		return IHCApiResponse(message="error").add_error(key="device", value="Device not fount").to_dict()

	driver = driver_factory(driver_type=device.device_driver, ip=device.device_host, relay=0, name=device.name)

	if on is True:
		driver.turn_on()
		return IHCApiResponse(message="success").add_data(key="device", value=driver.state).to_dict()
	
	if on is False:
		driver.turn_off()
		return IHCApiResponse(message="success").add_data(key="device", value=driver.state).to_dict()
