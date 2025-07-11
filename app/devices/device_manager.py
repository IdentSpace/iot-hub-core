def register_device(device_host: str, device_type: str, device_driver: str):
	from app.db.models import Device
	from app.db.session import get_session

	with get_session() as session:
		device = Device(device_host=device_host, device_type=device_type, device_driver=device_driver)
		session.add(device)
		session.commit()
		session.refresh(device)
		return device
	
def get_device(id: int):
	from app.db.models import Device
	from app.db.session import get_session
	from sqlmodel import select

	with get_session() as session:
		devices = session.exec(select(Device).where(Device.id == id)).first()
		return devices

def get_devices():
	from app.db.models import Device
	from app.db.session import get_session
	from sqlmodel import select

	with get_session() as session:
		devices = session.exec(select(Device)).all()
		return devices