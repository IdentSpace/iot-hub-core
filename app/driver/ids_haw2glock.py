from app.driver.types.device import DeviceBase, DeviceState
import serial
import threading
import time

class HAW2GLOCK(DeviceBase):

	def __init__(self, port, baudrate=115200, timeout=0.3):
		self.port = port
		self.baudrate = baudrate
		self.timeout = timeout
		self.serial = serial.Serial(port, baudrate, timeout=timeout)
		self.thread = None

	def connect(self):
		while True:
			try:
				self.serial = serial.Serial(
					port=self.port,
					baudrate=self.baudrate,
					timeout=self.timeout
				)
				print(f"NFC Reader verbunden an {self.port} @ {self.baudrate} Baud")
				break
			except serial.SerialException as e:
				print(f"FEHLER VERBINDUNG: {e}")
				time.sleep(2)
	
	def get_state(self):
		return super().get_state()
	
	def raw_command(self):
		return super().raw_command()
	
	def openLock(self, channel, address):
		cmd = b'\xA1' + channel.to_bytes(1, byteorder='big') + address.to_bytes(1, byteorder='big')
		self.serial.write(cmd)

	def getVersion(self):
		cmd = b'\x01'
		self.serial.write(cmd)
		response = self.serial.read(7)
		return response