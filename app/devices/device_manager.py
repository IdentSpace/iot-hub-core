def register_device(device_host: str, device_type: str, device_driver: str, device_name: str = None):
	from app.db.models import Device
	from app.db.session import get_session

	with get_session() as session:
		device = Device(name=device_name, device_host=device_host, device_type=device_type, device_driver=device_driver)
		session.add(device)
		session.commit()
		session.refresh(device)
		return device
	
def get_device(id: str):
	from app.db.models import Device
	from app.db.session import get_session
	from sqlmodel import select
	from sqlalchemy import text

	query = text("""
		SELECT 
			d.id, d.name, d.device_host, d.baudrate,
			d.device_driver, dd.name as device_driver_name,
			d.device_type, dt.name as device_type_name
		FROM device d
		LEFT JOIN device_type dt ON d.device_type = dt.id
		LEFT JOIN device_driver dd ON d.device_driver = dd.id
		WHERE d.id = REPLACE(:device_id,'-','')
		LIMIT 1
		""")

	with get_session() as session:
		raw_id = str(id)
		row = session.execute(query, {"device_id": raw_id}).fetchone()
		if row:
			return dict(row._mapping)
		return None

def get_devices():
	from app.db.models import Device
	from app.db.session import get_session
	from sqlmodel import select
	from sqlalchemy import text

	query = text("""
		SELECT 
			d.id, d.name, d.device_host, d.baudrate,
			d.device_driver, dd.name as device_driver_name,
			d.device_type, dt.name as device_type_name
		FROM device d
		LEFT JOIN device_type dt ON d.device_type = dt.id
		LEFT JOIN device_driver dd ON d.device_driver = dd.id
		""")

	with get_session() as session:
		rows = session.execute(query).fetchall()
		devices = [dict(row._mapping) for row in rows]
		return devices
	
def delete_device(id: str):
	from app.db.models import Device
	from app.db.session import get_session
	from sqlmodel import delete

	with get_session() as session:
		statement = delete(Device).where(Device.id == id)
		session.exec(statement)
		session.commit()
		return delete

def get_drivers():
	from app.db.models import DeviceDriver
	from app.db.session import get_session
	from sqlmodel import select

	with get_session() as session:
		drivers = session.exec(select(DeviceDriver)).all()
		return drivers

def get_types():
	from app.db.models import DeviceType
	from app.db.session import get_session
	from sqlmodel import select

	with get_session() as session:
		types = session.exec(select(DeviceType)).all()
		return types

def register_type(name: str, description: str = None):
	from app.db.models import DeviceType
	from app.db.session import get_session

	with get_session() as session:
		device_type = DeviceType(name=name, description=description)
		session.add(device_type)
		session.commit()
		session.refresh(device_type)
		return device_type

