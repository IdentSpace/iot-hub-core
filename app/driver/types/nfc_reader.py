from abc import ABC, abstractmethod
from datetime import datetime
from urllib.parse import urlencode


class NfcData:
	def __init__(self, uid: str):
		self.uid = uid
		self.timestamp = datetime.now()

	def toUrlQuery(self) -> str:
		params = {
			"UID": self.uid
		}

		params["timestamp"] = self.timestamp.isoformat()

		return "?" + urlencode(params)

class NfcReader(ABC):
	
	@abstractmethod
	def listen(self):
		pass

	@abstractmethod
	def listen_in_thread(self):
		pass