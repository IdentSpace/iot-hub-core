from sqlmodel import SQLModel, create_engine, Session, select
import os
import sys

def get_db_path(filename="data.db"):
    # PyInstaller erkennt man an _MEIPASS
    if hasattr(sys, "_MEIPASS"):
        # Speichert die DB neben der EXE
        return os.path.join(os.path.dirname(sys.executable), filename)
    else:
        # Normales Skript: aktueller Ordner
        return os.path.abspath(filename)

db_path = get_db_path()

# DATABASE_URL = "sqlite:///./data.db"
DATABASE_URL = f"sqlite:///{db_path}"

sync_engine  = create_engine(DATABASE_URL, echo=False, pool_size=5, max_overflow=10, connect_args={"check_same_thread": False})

def get_session():
	return Session(sync_engine )

def default_data():
	with get_session() as session:
		from app.db.models import SysValues, DeviceType, DeviceDriver, User, KeyType

		# Insert default device types
		has_sys_values = session.exec(select(SysValues)).first()
		if has_sys_values is None:
			default = [
				SysValues(name="WEBHOOK_1", value=""),
			]
			session.add_all(default)

		# Insert default device types
		has_device_types = session.exec(select(DeviceType)).first()
		if has_device_types is None:
			default = [
				DeviceType(name="base", description="default device type"),
				DeviceType(name="lamp", description="lamp"),
				DeviceType(name="machine", description="machine like in a workshop"),
				DeviceType(name="door", description="doors"),
				DeviceType(name="heater", description="heater"),
				DeviceType(name="datascanner", description="datascanner"),
				DeviceType(name="nfcreader", description="Basic NFC reader"),
				DeviceType(name="parking_barrier", description="Parking Barrier"),
			]
			session.add_all(default)
			
		# Insert default device drivers
		has_device_drivers = session.exec(select(DeviceDriver)).first()
		if has_device_drivers is None:
			default = [
				DeviceDriver(name="shelly_http", description="Shelly devices via HTTP"),
				DeviceDriver(name="default_datascanner", description="Default Data Scanner 1D / 2D"),
				DeviceDriver(name="default_nfcreader", description="Default NFC Scanner"),
				DeviceDriver(name="as1620", description="Parking Barrier from Automatic Systems"),
				DeviceDriver(name="feig_cpr0210", description="Feig CPR0210 NFC Reader"),
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
	SQLModel.metadata.create_all(sync_engine )
	default_data()
	# if create, insert default data here