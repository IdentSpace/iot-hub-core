import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import get_session
from app.db.models import Device, Room, TemperatureSchedule
from sqlmodel import SQLModel, create_engine, Session, select
from app.devices.device_manager import register_device

with get_session() as session:

	roomid_1 = "c35cf321c40a4cd99362a936edb7a885"
	roomid_2 = "397925f1a7e442fc8a7044fc8d8924f8"

	has_devices = session.exec(select(Device)).first()
	if has_devices is None:
		device = register_device(device_host="192.168.51.191", device_name="3D Printer (Test)", device_type="machine", device_driver="shelly_http")

	has_rooms = session.exec(select(Room)).first()
	if has_rooms is None:
		session.add(Room(id=roomid_1, name="Workshop", description="Makerspace"))
		session.add(Room(id=roomid_2, name="Office", description="Agency office"))

	session.add(TemperatureSchedule(room_id=roomid_1, target_temp=21.5, time_from="08:00:00", time_to="18:00:00", day_1=True, day_2=True, day_3=True, day_4=True, day_5=True, day_6=True, day_7=True))
	
	session.commit()