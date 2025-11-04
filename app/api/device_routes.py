from typing import Union
from uuid import UUID
from fastapi import APIRouter, status
from app.driver.driver_factory import driver_factory
from app.api.response import IHCApiResponse
from pydantic import BaseModel

router = APIRouter()

class Device(BaseModel):
	device_name: str
	device_host: str
	device_type: str
	device_driver: str

@router.post("/register")
def read_register_device(device: Device) :
	from app.devices.device_manager import register_device
	try:

		device = register_device(
			device_host=device.device_host,
			device_type=device.device_type,
			device_driver=device.device_driver,
			device_name=device.device_name
			)
		
		return IHCApiResponse(message="success").add_data(key="device", value=device).to_dict()
	
	except Exception as e:
		return IHCApiResponse(message="error").add_error(key="device", value=str(e)).to_dict()
		# status.HTTP_400_BAD_REQUEST

# TODO: Implement
@router.post("/update")
def req_update_device():
	pass


# TODO: Implement
@router.post("/delete")
def req_update_device():
	pass

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

@router.get("/{id}/delete")
def request_get_devices_state(id: UUID) :

	if id is None:
		return IHCApiResponse(message="error").add_error(key="device", value="Missing device id specified").to_dict()
	
	from app.devices.device_manager import delete_device
	device = delete_device(id=id)

	return IHCApiResponse(message="success").add_data(key="device", value=device).to_dict()

@router.get("/{id}/event")
def event_device(on: Union[bool, None] = None, id: Union[UUID, None] = None) :
	if on is None or id is None:
		return IHCApiResponse(message="error").add_error(key="device", value="Missing event or device id").to_dict()
	
	from app.devices.device_manager import get_device
	
	device = get_device(id=id)

	if not device:
		return IHCApiResponse(message="error").add_error(key="device", value="Device not found").to_dict()

	# TODO: fix driver laoding 
	driver = driver_factory(driver_type='as1620', ip=device.device_host, port=8081)
	# driver = driver_factory(driver_type='as1620', ip=device.device_host, relay=0, name=device.name)

	if on is True:
		driver.open_tree()
		# driver.turn_on()
		return IHCApiResponse(message="success").add_data(key="device", value=driver.state).to_dict()
	
	if on is False:
		# driver.turn_off()
		driver.close_tree()
		return IHCApiResponse(message="success").add_data(key="device", value=driver.state).to_dict()
