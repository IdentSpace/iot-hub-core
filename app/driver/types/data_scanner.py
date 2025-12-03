from abc import ABC, abstractmethod
from typing import Dict
from datetime import datetime
from urllib.parse import urlencode

class DataScannerData:
	def __init__(self, type: str, data: str, batch = None, rawData = None):
		self.type = type
		self.rawData = rawData
		self.data = data 
		self.batch = batch
		self.timestamp = datetime.now()
	
	def toUrlQuery(self) -> str:
		params = {
			"type": self.type,
			"data": self.data,
		}

		if(self.batch != None and self.batch != ''):
			params["batch"] = self.batch

		params["timestamp"] = self.timestamp.isoformat()

		return "?" + urlencode(params)

class DataScanner(ABC):
	
	@abstractmethod
	def listen(self):
		pass

	@abstractmethod
	def listen_in_thread(self):
		pass

class Parser:
	
	def gs1_datamatrix(code: str) -> Dict[str, str]:
		result = {}
		result["raw"] = code
		result["data"] = {}

		codeLength = len(code)

		result["length"] = codeLength

		if(codeLength < 14):
			result["success"] = False
			return result 

		FIXED_LENGTH_IDS = {
			"01": 14,  # GTIN
			"30": 8,   # Menge
		}

		VARIABLE_LENGTH_IDS = {
			"10": 20,  # Charge / Lot
		}

		result["data"]["01"] = None
		result["data"]["10"] = None

		i = 0
		while i < codeLength:
			id = code[i:i+2]
			i += 2

			if(id in FIXED_LENGTH_IDS):
				length = FIXED_LENGTH_IDS[id]
				value = code[i:i+length]
				result["data"][id] = value
				i += length
			elif(id in VARIABLE_LENGTH_IDS):
				c = code[i:]
				e = Parser.find_gs_position(c)
				length2 = i+e
				value = code[i:length2]
				result["data"][id] = value
				i = length2+1

		result["success"] = True
		return result
	
	def find_gs_position(s: str):
		GS = chr(29)
		return s.find(GS, 0)