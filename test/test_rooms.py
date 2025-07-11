import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import get_session
from app.db.models import Device, Room, TemperatureSchedule
from sqlmodel import SQLModel, create_engine, Session, select
from app.devices.device_manager import register_device
from app.core.room import Room, RoomUtils


rooms = RoomUtils.load_rooms()

for room in rooms:
	print(room)