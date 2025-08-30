import serial
import threading
from datetime import datetime
from typing import Dict
from app.state.dscanner import set_latest_dscanner_data

class DataScannerData:
    def __init__(self, type: str, data: Dict):
        self.type = type
        self.data = data 
        self.timestamp = datetime.now()
          

class DataScanner:

    def __init__(self, port, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial = serial.Serial(port,baudrate,timeout=1)
        self.thread = None

    def listen(self):
        while True:
            if self.serial.in_waiting > 0:
                data = self.serial.readline().decode('utf-8').strip()
                if data:
                    print(f"Received data: {data}")
                    gs1DM = Parser.gs1_datamatrix(data)
                    if(gs1DM["success"] == True):
                        set_latest_dscanner_data(DataScannerData(type="datamatrix_gs1",data=data))
                    else:
                        set_latest_dscanner_data(DataScannerData(type="raw",data=data))
    
    def listen_in_thread(self):
        self.thread = threading.Thread(target=self.listen)
        self.thread.daemon = True
        self.thread.start()
        return self
    
    def close(self):
        if self.serial.is_open:
            self.serial.close()
        if self.thread:
            self.thread.join()

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