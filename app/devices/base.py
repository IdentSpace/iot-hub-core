from abc import ABC, abstractmethod

class DeviceState:
	ONLINE = "online"
	OFFLINE = "offline"
	ERROR = "error"
	NONE = "none"

	def __init__(self, state: str = NONE, message: str = "", raw_data: dict = None, power_state: bool = None):
		self.state = state
		self.message = message
		self.raw_data = raw_data if raw_data is not None else {}
		self.power_state = power_state

class BaseDevice(ABC):

	@abstractmethod
	def turn_on(self):
		pass
	
	@abstractmethod
	def turn_off(self):
		pass

	@abstractmethod
	def get_state(self) -> DeviceState:
		pass

	#TODO: RAW COMMAND


