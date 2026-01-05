from app.driver.types.data_scanner import DataScanner, Parser, DataScannerData
from app.driver.types.device import DeviceBase, DeviceState
from app.state.dscanner import set_latest_dscanner_data
import serial
import threading
import time

class DefaultDataScanner(DeviceBase, DataScanner):

	def __init__(self, args:dict):
		self.port = args.get("port", None)
		self.baudrate = args.get("baudrate", 9600) or 9600
		self.timeout = args.get("timeout", 1)
		self.thread = None
		self.serial = None

	def listen(self):
		while True:
			try:
				if not self.serial or not self.serial.is_open:
					try:
						self.serial = serial.Serial(
							port=self.port,
							baudrate=self.baudrate,
							timeout=self.timeout
						)
					except serial.SerialException as e:
						time.sleep(2)
						continue

				if self.serial.in_waiting > 0:
					try:
						data = self.serial.readline().decode('utf-8', errors="replace").strip()
						if data:
							print(f"Received data: {data}")
							gs1DM = Parser.gs1_datamatrix(data)
							if(gs1DM["success"] == True):
								set_latest_dscanner_data(DataScannerData(type="dmgs1", data=gs1DM["data"]["01"], batch=gs1DM["data"]["10"]))
							else:
								set_latest_dscanner_data(DataScannerData(type="raw",data=data))
					except Exception as e:
						print("Error Scanner Readline: " + str(e))
						continue
			except Exception as e:
				print("FEHLER LISTEN")
				self.serial.close()
				print(e)
				time.sleep(2)
				continue

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

	def get_state(self):
		return DeviceState(state=DeviceState.NONE, message="NOT IMPLEMENTED", raw_data={})
	
	def raw_command(self):
		return super().raw_command()