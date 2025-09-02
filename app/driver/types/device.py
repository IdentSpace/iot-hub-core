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

class DeviceBase(ABC):

	@abstractmethod
	def get_state(self)->DeviceState:
		pass

	@abstractmethod
	def raw_command(self):
		pass

	def list_bases(self):
		return[
            base.__name__
            for base in type(self).__mro__
            if issubclass(base,ABC) 
            and base is not ABC
			and base is not DeviceBase
            and base is not type(self)
        ]

class Default(DeviceBase):
	def __init__(self, ip: str = "", relay: int = 0, name: str = "DefaultDevice"):
		self.state = None

	def turn_on(self):
		return self.state
	
	def turn_off(self):
		return self.state

	def get_state(self) -> DeviceState:
		return DeviceState(state=DeviceState.NONE, message="NOT IMPLEMENTED", raw_data={})
