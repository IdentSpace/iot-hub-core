from sqlmodel import SQLModel, create_engine, Session, select

DATABASE_URL = "sqlite:///./data.db"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
	return Session(engine)

def default_data():
	with get_session() as session:
		from app.db.models import DeviceType, DeviceDriver, User, KeyType

		# Insert default device types
		has_device_types = session.exec(select(DeviceType)).first()
		if has_device_types is None:
			default = [
				DeviceType(name="base", description="default device type"),
				DeviceType(name="lamp", description="lamp"),
				DeviceType(name="machine", description="machine like in a workshop"),
				DeviceType(name="door", description="doors"),
				DeviceType(name="heater", description="heater"),
			]
			session.add_all(default)
			
		# Insert default device drivers
		has_device_drivers = session.exec(select(DeviceDriver)).first()
		if has_device_drivers is None:
			default = [
				DeviceDriver(name="shelly_http", description="Shelly devices via HTTP"),
			]
			session.add_all(default)

		# Insert default user
		has_users = session.exec(select(User)).first()
		if has_users is None:
			default = [
				User(username="admin", password="admin"),
			]
			session.add_all(default)

		# Insert default key types
		has_key_type = session.exec(select(KeyType)).first()
		if has_key_type is None:
			default = [
				KeyType(name="nfc_basic", description="basic nfc id from mifare classic etc."),
			]
			session.add_all(default)

		session.commit()

def initialize_database():
	from . import models
	SQLModel.metadata.create_all(engine)
	default_data()
	# if create, insert default data here