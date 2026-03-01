from abc import ABC, abstractmethod
from typing import Dict
from datetime import datetime
from urllib.parse import urlencode
from urllib.parse import quote

class DataScannerData:
	def __init__(self, type: str, data: str, batch = None, rawData = None):
		self.type = type
		self.rawData = rawData
		self.data = data 
		self.batch = batch
		self.timestamp = datetime.now()

	def quote_safe(self, value: str) -> str:
		return quote(value, safe='')
	
	def toUrlQuery(self) -> str:
		params = {
			"type": self.quote_safe(str(self.type)),
			"data": self.quote_safe(str(self.data)),
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
    @staticmethod
    def find_gs_position(s: str):
        GS = chr(29)
        pos = s.find(GS)
        # Wenn kein GS gefunden wurde, ist das Ende des Strings die Grenze
        return pos if pos != -1 else len(s)

    @staticmethod
    def gs1_datamatrix(code: str) -> Dict[str, any]:
        result = {"raw": code, "data": {}, "success": False}
        
        # Bekannte Application Identifier (AIs)
        FIXED_LENGTH_IDS = {
            "01": 14,  # GTIN
            "17": 6,   # Verfallsdatum (YYMMDD)
            "11": 6,   # Produktionsdatum (YYMMDD)
        }
        VARIABLE_LENGTH_IDS = {
            "10": 20,  # Charge / Lot
            "21": 20,  # Serialnummer
            "30": 8,   # Menge
        }

        try:
            i = 0
            code_len = len(code)
            
            while i < code_len:
                # AI extrahieren (meist 2 Stellen)
                ai = code[i:i+2]
                i += 2

                if ai in FIXED_LENGTH_IDS:
                    length = FIXED_LENGTH_IDS[ai]
                    result["data"][ai] = code[i:i+length]
                    i += length
                elif ai in VARIABLE_LENGTH_IDS:
                    remainder = code[i:]
                    # Suche nach GS oder Ende des Strings
                    relative_end = Parser.find_gs_position(remainder)
                    
                    # Begrenzung durch max. erlaubte Länge des AIs
                    actual_length = min(relative_end, VARIABLE_LENGTH_IDS[ai])
                    
                    result["data"][ai] = remainder[:actual_length]
                    # Springe hinter den Wert + eventuellen GS (1 Zeichen)
                    i += actual_length
                    if i < code_len and code[i] == chr(29):
                        i += 1 
                else:
                    # Unbekannter AI: Hier müsste man theoretisch abbrechen 
                    # oder eine komplexere AI-Tabelle (3-4 stellig) nutzen
                    break

            # Validierung: GTIN (01) ist meist Pflicht
            if "01" in result["data"]:
                result["success"] = True
                
            return result

        except Exception as e:
            print(f"Error parsing Datamatrix: {e}")
            return result