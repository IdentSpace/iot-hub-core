from app.driver.types.device import DeviceBase, DeviceState
import requests
import logging

logger = logging.getLogger("uvicorn.error")
# GEN 2 RPC API
class Shelly(DeviceBase):
	def __init__(self, args:dict):
		self.ip = args.get("device_host", None)
		self.relay = args.get("channel", 0)
		self.name = args.get("name", "ShellyDevice")
		self.state = None
		self.type = "shelly_http"

	def _request(self, action: str):
		if(self.ip == None):
			logger.error(f"Device {self.name} Error(E1): ip is none")
			return None
		
		url = f"http://{self.ip}/rpc/{action}"
		logger.info(f"Device {self.name}: {url}")
		try:
			response = requests.get(url, timeout=2)
			if response.status_code == 200:
				return response
			else:
				logger.error(f"Device {self.name} Error(E2): reponse missing/error")
				return None

		except Exception as e:
			self.state = DeviceState(state=DeviceState.ERROR, message=str(e), raw_data={})
			logger.error(f"Device {self.name} Error(E2): " + str(e))
			return None

	def turn_on(self):
		logger.info(f"{self.name} try on")
		self._request(f"Switch.Set?id={self.relay}&on=true")
		return self.state
	
	def turn_off(self):
		logger.info(f"{self.name} try off")
		self._request(f"Switch.Set?id={self.relay}&on=false")
		return self.state
	
	def raw_command(self):
		pass
	
	def get_state(self):
		try:
			response = self._request('Shelly.GetStatus?id=0')
			if response.status_code == 200:
				data = response.json()
				power_state = data.get(f"switch:{self.relay}", {}).get("output")
				power_state = True if power_state > 0 else False
				self.state = DeviceState(state=DeviceState.ONLINE, message="SUCCESS", power_state=power_state, raw_data=response.json())
				return self.state
			else:
				self.state = DeviceState(state=DeviceState.ERROR, message="Unable to get state", raw_data=response.json())
				return self.state
		except Exception as e:
			logger.error(f"[ERROR] Shelly {self.name}: {e}")
			self.state = DeviceState(state=DeviceState.ERROR, message=str(e), raw_data={})
			return self.state
		
	def web_command(self,cmd: str, arg: str):
		if cmd == 'switch':
			if(arg == 'on'):
				self.turn_on()
			if(arg == 'off'):
				self.turn_off()