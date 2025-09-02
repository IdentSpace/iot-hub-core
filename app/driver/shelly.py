from app.driver.types.device import DeviceBase, DeviceState
import requests

# GEN 2 RPC API
class Shelly(DeviceBase):
	def __init__(self, ip: str = "", relay: int = 0, name: str = "ShellyDevice"):
		self.ip = ip
		self.relay = relay
		self.name = name
		self.state = None
		self.type = "shelly_http"

	def _request(self, action: str):
		url = f"http://{self.ip}/rpc/Switch.Set?id={self.relay}&on={action}"
		try:
			response = requests.get(url, timeout=2)
			if response.status_code == 200:
				pass
			self.get_state()

		except Exception as e:
			self.state = DeviceState(state=DeviceState.ERROR, message=str(e), raw_data={})
			print(f"[ERROR] Shelly {self.name}: {e}")

	def turn_on(self):
		self._request("true")
		return self.state
	
	def turn_off(self):
		self._request("false")
		return self.state
	
	def raw_commnand(self):
		pass
	
	def get_state(self):
		url = f"http://{self.ip}/rpc/Shelly.GetStatus?id=0"
		try:
			response = requests.get(url, timeout=2)
			if response.status_code == 200:
				data = response.json()
				power_state = data.get("switch:0", {}).get("apower")
				power_state = True if power_state > 0 else False
				self.state = DeviceState(state=DeviceState.ONLINE, message="SUCCESS", power_state=power_state, raw_data=response.json())
				return self.state
			else:
				self.state = DeviceState(state=DeviceState.ERROR, message="Unable to get state", raw_data=response.json())
				return self.state
		except Exception as e:
			print(f"[ERROR] Shelly {self.name}: {e}")
			self.state = DeviceState(state=DeviceState.ERROR, message=str(e), raw_data={})
			return self.state