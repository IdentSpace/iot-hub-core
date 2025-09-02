from abc import ABC, abstractmethod
from datetime import datetime

class NfcData:
	def __init__(self, uid: str):
		self.uid = uid
		self.timestamp = datetime.now()

class NfcReader(ABC):
    pass