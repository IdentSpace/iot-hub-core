from app.db.models import Room as RoomModel
from app.db.session import get_session
from uuid import UUID, uuid4
from sqlmodel import select
from typing import List

class Room:
	def __init__(self, room: 'UUID | RoomModel'):
		if isinstance(room, RoomModel):
			self.id = room.id
			self.room_model = room
		else:
			self.id = room
			self.room_model = None
			self.__loadself()

		self.sensors_doors = []
		self.sensors_heaters = []
		self.sensors_lights = []
		self.sensors_temperature = []
		self.sensors_windows = []
		self.sensors_desks = []

	def __loadself(self):
		if not self.room_model:
			with get_session() as session:
				self.room_model = session.exec(select(RoomModel).where(RoomModel.id == self.id)).first()
				if not self.room_model:
					raise ValueError(f"Room with ID {self.id} not found.")
		print(f"Loading room with ID: {self.id}")
	
	def load_sensors(self):
		print(f"Loading sensors for room ID: {self.id}")
		# TODO: load heaters
		# TODO: load temperature

	def regulate_temperature(self):
		if self.sensors_lights and self.sensors_temperature:
			print(f"Regulating temperature for room ID: {self.id}")
			# if temp < min_temp, turn on heater
			# if temp > max_temp, turn off heater
		else:
			print(f"No sensors available for temperature regulation in room ID: {self.id}")

	def __str__(self):
		return f"Room: id={self.id} name={self.room_model.name if self.room_model else 'Unknown'}"

class RoomUtils:
	def load_rooms() -> List[Room]:
		with get_session() as session:
			rooms = session.exec(select(RoomModel)).all()

			return [Room(room) for room in rooms]
