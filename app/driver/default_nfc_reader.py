from app.driver.types.nfc_reader import NfcReader,NfcData
from app.driver.types.device import DeviceBase, DeviceState
from app.state.nfc import set_latest_nfc_data
import serial
import threading
import time
import logging

logger = logging.getLogger("uvicorn.error")

class DefaultNfcReader(DeviceBase, NfcReader):
	def __init__(self, args:dict):
		self.port = args.get("port", None)
		self.baudrate = args.get("baudrate", 115200)
		self.timeout = args.get("timeout", 1)
		self.serial = None
		self.thread = None
		self.name = "DafaultNFCReader"
		self._stop_event = threading.Event()

	def connect(self):
		while True:
			try:
				self.serial = serial.Serial(
					port=self.port,
					baudrate=self.baudrate,
					timeout=self.timeout
				)
				logger.info(f"NFC Reader verbunden an {self.port} @ {self.baudrate} Baud")
				break
			except serial.SerialException as e:
				logger.error(f"FEHLER VERBINDUNG: {e}")
				time.sleep(2)

	# TODO: implement 
	def heartbeat(self):
		pass
		
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
					set_latest_nfc_data(NfcData(uid=data))
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
		logger.info(f"Device {self.name}: close serial/thread")
		self._stop_event.set()
		if self.serial and self.serial.is_open:
			self.serial.close()
		if self.thread:
			self.thread.join()

	def get_state(self):
		return DeviceState(state=DeviceState.NONE, message="NOT IMPLEMENTED", raw_data={})
	
	def raw_command(self):
		return super().raw_command()
