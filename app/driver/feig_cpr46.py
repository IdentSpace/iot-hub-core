from app.driver.types.device import DeviceBase, DeviceState
from app.driver.types.nfc_reader import NfcReader,NfcData
from app.state.nfc import set_latest_nfc_data
import serial
import threading
import time
import logging

logger = logging.getLogger("uvicorn.error")

INVENTORY_FRAME = bytes.fromhex("02 00 09 00 B0 01 00 CA 86")

class CPR46(DeviceBase):

	def __init__(self, args:dict):
		self.port = args.get("port")
		self.baudrate = args.get("baudrate", 38400) or 38400
		self.timeout = args.get("timeout", 0.3)
		self.serial = None
		self.thread = None
		self.isCMD = False
		self.deviceId = args.get("id", None)
		self.name = "FEIG CPR46.10"
		self._stop_event = threading.Event()

	def connect(self):
		while True:
			try:
				self.serial = serial.Serial(
					port=self.port,
					baudrate=self.baudrate,
					timeout=self.timeout,
					bytesize=serial.EIGHTBITS,
					parity=serial.PARITY_EVEN,
					stopbits=serial.STOPBITS_ONE
				)
				logger.info(f"NFC Reader verbunden an {self.port} @ {self.baudrate} Baud")
				break
			except serial.SerialException as e:
				logger.info(f"FEHLER VERBINDUNG: {e}")
				time.sleep(2)
				
	def heartbeat(self):
		pass
				
	def listen(self):
		if not self.serial or not self.serial.is_open:
			self.connect()

		last_check = time.time()
		self.heartbeat()

		while True:
			try:
				self.serial.write(INVENTORY_FRAME)
				time.sleep(0.05) # 50 ms delay
				response = self.serial.read(64)

				if response:
					uid = CPR46.parse_inventory_response(response)
					if uid:
						set_latest_nfc_data(NfcData(uid=uid, deviceId=self.deviceId))
						logger.info(f"Device {self.name} RX: {uid}")
						time.sleep(1)

			except serial.SerialException as e:
				logger.error(f"Device {self.name} Error(R2): " + str(e))
				self.serial.close()
				self.connect()
				continue
			except Exception as e:
				logger.error(f"Device {self.name} Error(R3): " + str(e))
				self.serial.close()
				time.sleep(2)
				continue

	def listen_in_thread(self):
		self.thread = threading.Thread(target=self.listen)
		self.thread.daemon = True
		self.thread.start()
		return self

	def crc16_ccitt(data: bytes) -> int:
		crc = 0xFFFF
		for byte in data:
			crc ^= byte
			for _ in range(8):
				if crc & 1:
					crc = (crc >> 1) ^ 0x8408
				else: 
					crc >>= 1
		return crc & 0xFFFF
	
	def parse_inventory_response(data):
		if len(data) < 10:
			return None
		
		alengt = int.from_bytes(data[1:3], byteorder='big')
		if(alengt != len(data)):
			logger.info("Fehlerhafte Antwortlänge: " + str(alengt) + " != " + str(len(data)))

		status = data[5]

		if(status != 0x00):
			logger.info("Fehlerhafter Status: " + str(status))
			return None
		
		data_sets = data[6]

		if(data_sets < 1 or data_sets > 1):
			logger.info("Keine Daten-Sets oder zu viele Daten-Sets: " + str(data_sets))
			return None


		tr_type = data[7]
		tr_info = data[8]
		opt_info = data[9]

		uid_end = alengt-2
		uid = None

		logger.info(f"Status: {status}, Data Sets: {data_sets} TR Type: {tr_type}, TR Info: {tr_info}, Opt Info: {opt_info}")

		if(tr_type == 0x04):
			c_level = opt_info & 0x03

			uid_len = None

			if c_level == 0x00:
				uid_len = 4
			elif c_level == 0x01:
				uid_len = 7
			elif c_level == 0x02:
				uid_len = 10
			
			if(uid_len):
				uid = data[uid_end-uid_len:uid_end]
				return uid[::-1].hex().upper()
			
			uid = data[uid_end-4:uid_end]
		
		if(uid == None):
			return data.hex('').upper()

		uid = uid.hex().upper()
		return uid[::-1]
	
	def get_state(self):
		return super().get_state()
	
	def raw_command(self):
		return super().raw_command()
	
	def getVersion(self):
		cmd = b'\x01'
		self.serial.write(cmd)
		response = self.serial.read(7)
		return response