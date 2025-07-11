from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from app.core.room import Room, RoomUtils

scheduler = BackgroundScheduler()


def start_scheduler():
	rooms = RoomUtils.load_rooms()
	print(f"Loaded {len(rooms)} rooms for scheduling.")

	# TODO: await for x sec. (?)

	for room in rooms:
		scheduler.add_job(room.regulate_temperature, 'interval', seconds=900) # TODO: add id='temperature_control_job'
	
	scheduler.start()