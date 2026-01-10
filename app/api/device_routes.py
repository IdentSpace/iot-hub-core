from typing import Union
from uuid import UUID
from fastapi import APIRouter, status
from app.driver.driver_factory import driver_factory
from app.api.response import IHCApiResponse
from pydantic import BaseModel

router = APIRouter()

# TODO: kann ich das DB Model verwenden statt die Klasse?
class Device(BaseModel):
	device_name: str
	device_host: str
	device_type: int
	device_driver: int

class DeviceType(BaseModel):
	name: str
	description: str

@router.post("/register/device")
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

@router.post("/register/type")
def req_register_type(type: DeviceType) :
	from app.devices.device_manager import register_type
	try:

		type = register_type(
			name=type.name,
			description=type.description
			)
		
		return IHCApiResponse(message="success").add_data(key="device_type", value=type).to_dict()
	
	except Exception as e:
		return IHCApiResponse(message="error").add_error(key="device_type", value=str(e)).to_dict()
		# status.HTTP_400_BAD_REQUEST

@router.post("/update")
def req_update_device(data: dict):
	from app.devices.device_manager import update_device

	if "id" not in data:
		return IHCApiResponse(message="error").add_error(key="device", value="Missing device id").api_response()

	device_id = data.pop("id")
	device = update_device(id=device_id, data=data)
	if not device:
		return IHCApiResponse(message="error").add_error(key="device", value="Device not found").api_response()
	
	return IHCApiResponse(message="success").add_data(key="device", value="").api_response()

@router.get("/list")
def request_get_devices() :
	from app.devices.device_manager import get_devices
	devices = get_devices()
	return IHCApiResponse(message="success").add_data(key="device", value=devices).to_dict()

@router.get("/list/drivers")
def request_get_devices() :
	from app.devices.device_manager import get_drivers
	drivers = get_drivers()
	return IHCApiResponse(message="success").add_data(key="device_drivers", value=drivers).to_dict()

@router.get("/list/types")
def request_get_devices() :
	from app.devices.device_manager import get_types
	types = get_types()
	return IHCApiResponse(message="success").add_data(key="device_types", value=types).to_dict()

@router.get("/{id}/state")
def request_get_devices_state(id: UUID) :

	if id is None:
		return IHCApiResponse(message="error").add_error(key="device", value="Missing device id specified").to_dict()
	
	from app.devices.device_manager import get_device
	device = get_device(id=id)

	if not device:
		return IHCApiResponse(message="error").add_error(key="device", value="Device not found").to_dict()

	driver = driver_factory(driver_type=device["device_driver_name"], args=device)
	device = driver.get_state()
	return IHCApiResponse(message="success").add_data(key="device", value=device).to_dict()

@router.get("/{id}/delete")
def request_get_delete_state(id: UUID) :

	if id is None:
		return IHCApiResponse(message="error").add_error(key="device", value="Missing device id specified").to_dict()
	
	from app.devices.device_manager import delete_device
	device = delete_device(id=id)

	return IHCApiResponse(message="success").add_data(key="device", value=device).to_dict()

@router.get("/{id}/event")
def event_device(cmd: Union[str, None] = None, arg: Union[str, None] = None, id: Union[UUID, None] = None) :
	if cmd is None or id is None:
		return IHCApiResponse(message="error").add_error(key="device", value="Missing event or device id").to_dict()
	
	from app.devices.device_manager import get_device
	
	device = get_device(id=id)

	if not device:
		return IHCApiResponse(message="error").add_error(key="device", value="Device not found").to_dict()

	driver = driver_factory(driver_type=device["device_driver_name"], args=device)

	driver.web_command(cmd=cmd, arg=arg)
	return IHCApiResponse(message="success").add_data(key="device", value=driver.get_status()).to_dict()