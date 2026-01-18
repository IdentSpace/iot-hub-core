from app.driver.types.data_scanner import DataScanner, Parser, DataScannerData
from app.driver.types.device import DeviceBase, DeviceState
from app.state.dscanner import set_latest_dscanner_data
import serial
import threading
import time
import logging

logger = logging.getLogger("uvicorn.error")

class DefaultDataScanner(DeviceBase, DataScanner):

	def __init__(self, args:dict):
		self.port = args.get("port", None)
		self.baudrate = args.get("baudrate", 9600) or 9600
		self.timeout = args.get("timeout", 1)
		self.thread = None
		self.serial = None
		self.name = "DafaultDataScanner"
		self._stop_event = threading.Event()

	def listen(self):
		while not self._stop_event.is_set():
			try:
				if not self.serial or not self.serial.is_open:
					if self.serial:
						self.serial.close()
						self.serial = None
					try:
						self.serial = serial.Serial(
							port=self.port,
							baudrate=self.baudrate,
							timeout=self.timeout
						)
					except serial.SerialException as e:
						logger.error(f"Device {self.name} Error(R1): " + str(e))
						time.sleep(2)
						continue

				data_bytes = self.serial.readline()
				if not data_bytes:
					continue

				data = data_bytes.decode("utf-8", errors="replace").strip()
				if not data:
					continue

				try:
					logger.info(f"Device {self.name} RX: {data}")
					gs1DM = Parser.gs1_datamatrix(data)
					if(gs1DM["success"] == True):
						set_latest_dscanner_data(DataScannerData(type="dmgs1", data=gs1DM["data"]["01"], batch=gs1DM["data"]["10"]))
					else:
						set_latest_dscanner_data(DataScannerData(type="raw",data=data))
				except Exception as e:
					logger.error(f"Device {self.name} Error(R2): " + str(e))
					continue
			except Exception as e:
				logger.error(f"Device {self.name} Error(R3): " + str(e))
				self.serial.close()
				time.sleep(2)
				continue

	def listen_in_thread(self):
		try:
			logger.info(f"Device {self.name}: listen in thread")
			self.thread = threading.Thread(target=self.listen, daemon=True)
			self.thread.start()
			return self
		except Exception as e:
			logger.error(f"Device {self.name} Error(R4): " + str(e))
			return self


	def close(self):
		logger.info(f"Device {self.name}: close serial")
		self._stop_event.set()
		if self.serial and self.serial.is_open:
			self.serial.close()
		if self.thread:
			self.thread.join()

	def get_state(self):
		return DeviceState(state=DeviceState.NONE, message="NOT IMPLEMENTED", raw_data={})
	
	def raw_command(self):
		return super().raw_command()