import serial
import threading
from datetime import datetime
from app.state.nfc import set_latest_nfc_data

class NfcData:
	def __init__(self, uid: str):
		self.uid = uid
		self.timestamp = datetime.now()

class NfcReader:
	def __init__(self, port="COM6", baudrate=9600):
		self.port = port
		self.baudrate = baudrate
		self.serial = serial.Serial(port, baudrate, timeout=1)
		self.thread = None

	def listen(self):
		while True:
			if self.serial.in_waiting > 0:
				data = self.serial.readline().decode('utf-8').strip()
				if data:
					print(f"Received NFC data: {data}")
					set_latest_nfc_data(NfcData(uid=data))
					# Here you can add logic to handle the received NFC data
					# For example, you could trigger an event or store the data in a database


	def listen_in_thread(self):
		self.thread = threading.Thread(target=self.listen)
		self.thread.daemon = True
		self.thread.start()
		return self
	
	def close(self):
		if self.serial.is_open:
			self.serial.close()
			print("NFC Reader closed.")
		if self.thread:
			self.thread.join()
			print("NFC Reader thread joined.")