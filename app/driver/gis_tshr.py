from app.driver.types.nfc_reader import NfcReader,NfcData
from app.driver.types.device import DeviceBase, DeviceState
from app.state.nfc import set_latest_nfc_data
import serial
import threading
import time
import logging

logger = logging.getLogger("uvicorn.error")

class GiSTSHR(DeviceBase, NfcReader):
	def __init__(self, args:dict):
		self.port = args.get("port", None)
		self.baudrate = args.get("baudrate", 115200)
		self.timeout = args.get("timeout", 1)
		self.serial = None
		self.thread = None
		self.isCMD = False
		self.deviceId = args.get("id", None)
		self.name = "DafaultNFCReader"
		self._stop_event = threading.Event()

	def connect(self):
		while True:
			try:
				self.serial = serial.Serial(
					port=self.port, # oder dein tatsächlicher Port 
					baudrate=self.baudrate, 
					parity=serial.PARITY_NONE, 
					stopbits=serial.STOPBITS_ONE, 
					bytesize=serial.EIGHTBITS, 
					timeout=0.3 # 300 ms laut Screenshot 
					)
				self.control_leds(red=False,green=False,yellow=True)
				time.sleep(0.3)
				self.control_leds(red=False,green=True,yellow=False)
				time.sleep(0.3)
				self.control_leds(red=True,green=False,yellow=False)
				time.sleep(0.3)
				self.control_leds(red=False,green=False,yellow=True)
				logger.info(f"NFC Reader verbunden an {self.port} @ {self.baudrate} Baud")
				break
			except serial.SerialException as e:
				logger.error(f"FEHLER VERBINDUNG: {e}")
				time.sleep(2)

	# TODO: implement 
	def heartbeat(self):
		pass
	
		# last_check = time.time()
		# self.heartbeat()
		# set_latest_nfc_data(NfcData(uid=data2))
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
							parity=serial.PARITY_NONE, 
							stopbits=serial.STOPBITS_ONE, 
							bytesize=serial.EIGHTBITS, 
							timeout=self.timeout
						)
						self.control_leds(red=False,green=False,yellow=True)
						time.sleep(0.3)
						self.control_leds(red=False,green=True,yellow=False)
						time.sleep(0.3)
						self.control_leds(red=True,green=False,yellow=False)
						time.sleep(0.3)
						self.control_leds(red=False,green=False,yellow=True)
					except serial.SerialException as e:
						logger.error(f"Device {self.name} Error(R1): " + str(e))
						time.sleep(2)
						continue

				if self.isCMD:
					continue

				data_bytes = self.serial.readline()
				if not data_bytes:
					continue

				data = data_bytes.decode("utf-8", errors="replace").strip()
				if not data:
					continue

				try:
					logger.info(f"Device {self.name} RX: {data}")
					set_latest_nfc_data(NfcData(uid=data, deviceId=self.deviceId))
					self.control_leds(red=False, green=True, yellow=True)
					time.sleep(0.3)
					self.control_leds(red=False, green=False, yellow=True)
					time.sleep(0.3)
					self.control_leds(red=False, green=True, yellow=True)
					time.sleep(0.3)
					self.control_leds(red=False, green=False, yellow=True)
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
	
	
	def crc(self,data):
		return sum(data) & 0xFF 

	def set_led(self):
		# STX, ADR, CMD, LEN, ROT, GRUEN, GELB 
		cmd = bytearray([0x02, 0x01, 0x03, 0x03, 0x01, 0x00, 0x00])
		crc = cmd[1] ^ cmd[2] ^ cmd[3] ^ cmd[4] ^ cmd[5] ^ cmd[6]
		cmd.append(crc)
		logger.info("LED ROT %s", cmd)
		self.serial.write(cmd)
		resp = self.serial.read(20)
		logger.info("LED Antwort: %s", resp)

	def set_led_direct(self, red:bool = False, green:bool = False, yellow:bool = False):
		self.serial.write(b'~R1' if red else b'~R0')
		self.serial.write(b'~G1' if green else b'~G0')
		# self.serial.write(b'~Y1' if yellow else b'~Yx')

	def set_led_low_level(self,mask, data):
		"""Nutzt den Set IO Befehl F6h [cite: 55]"""
		stx = 0x02
		addr = 0x01
		cmd = 0xF6
		length = 0x02
		
		# XOR Prüfsumme über Adresse, CMD, Anzahl und Daten 
		lrc = addr ^ cmd ^ length ^ mask ^ data
		
		packet = bytearray([stx, addr, cmd, length, mask, data, lrc])
		self.serial.write(packet)

	def control_leds(self,red=None, green=None, yellow=None, buzzer=None):
		"""
		Steuert die LEDs des GiS Readers.
		Parameter: True (An), False (Aus), None (Unverändert lassen)
		"""
		mask = 0x00
		data = 0x00
		
		# Bit-Belegung laut Protokoll:
		# Bit 5: Rot, Bit 6: Grün, Bit 7: Gelb
		led_config = {
			5: red,
			6: green,
			7: yellow
		}
		
		for bit, state in led_config.items():
			if state is not None:
				mask |= (1 << bit)       # Maske setzen: Dieses Bit soll geändert werden
				if state:
					data |= (1 << bit)   # Daten setzen: Bit auf 1 (An)
		
		# Wenn keine LED geändert werden soll, abbrechen
		if mask == 0:
			return

		# Protokoll-Rahmen Aufbau[cite: 16, 23, 24]:
		stx = 0x02
		addr = 0x01
		cmd = 0xF6
		length = 0x02
		
		# XOR Prüfsumme über Adresse, CMD, Anzahl und Daten 
		lrc = addr ^ cmd ^ length ^ mask ^ data
		
		packet = bytearray([stx, addr, cmd, length, mask, data, lrc])
		self.isCMD = True
		self.serial.write(packet)
		self.serial.read(5)
		self.isCMD = False
		# Antwort vom Gerät lesen (optional) [cite: 16]
		# return self.serial.read(5)

	def make_red_the_default(self):
		# STX, Adresse (01h), CMD (06h - Write EEPROM), Anzahl (02h)
		# Daten: Startadresse im EEPROM, Wert
		stx = 0x02
		addr = 0x01
		cmd = 0x06
		length = 0x02
		
		# Register 0x02 im EEPROM steuert oft den Default-Zustand der IOs
		# Wert 0x20 = Bit 5 gesetzt (Rote LED an)
		reg_addr = 0x02 
		val = 0x20      
		
		lrc = addr ^ cmd ^ length ^ reg_addr ^ val
		
		packet = bytearray([stx, addr, cmd, length, reg_addr, val, lrc])
		self.serial.write(packet)
		
		response = self.serial.read(5)
		if response and response[2] == 0x00:
			print("Erfolg: Rote LED als Standard beim Starten gespeichert.")
		else:
			print(f"Fehler beim Speichern. Code: {response.hex() if response else 'Keine Antwort'}")


	def set_mode(self):
		cmd = bytearray([0x07, 0x10, 0x01])
		cmd.append(self.crc(cmd))
		logger.info("SET MODE %s", cmd)

		self.serial.write(cmd)
		resp = self.serial.read(4)
		logger.info("Antwort: %s", resp)

	def ping(self):
		# STX, Adresse, CMD(F0), Anzahl(0)
		cmd = bytearray([0x02, 0x01, 0xF0, 0x00])
		crc = cmd[1] ^ cmd[2] ^ cmd[3] # XOR über Adresse, CMD, Anzahl 
		cmd.append(crc) 
		logger.info("PING %s", cmd)
		self.serial.write(cmd)
		resp = self.serial.read(50)
		logger.info("PING Antwort: %s", resp)