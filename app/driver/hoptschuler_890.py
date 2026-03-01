from app.driver.types.nfc_reader import NfcReader,NfcData
from app.driver.types.device import DeviceBase, DeviceState
from app.state.nfc import set_latest_nfc_data
import serial
import threading
import time
import logging

logger = logging.getLogger("uvicorn.error")

class HoptSchuler890(DeviceBase, NfcReader):

	cmd_start_polling = bytes([0x01, 0x01, 0x00, 0x01, 0x5D, 0x01, 0x5D])

	def __init__(self, args:dict):
		self.port = args.get("port", None)
		self.baudrate = args.get("baudrate", 115200)
		self.timeout = 0.4
		self.serial = None
		self.thread = None
		self.name = "HoptSchuler890"
		self._stop_event = threading.Event()

	def connect(self):
		while True:
			try:
				self.serial = serial.Serial(
					port=self.port,
					baudrate=self.baudrate,        # Standard-Baudrate laut Handbuch
					bytesize=serial.EIGHTBITS,
					parity=serial.PARITY_NONE,
					stopbits=serial.STOPBITS_ONE,
					timeout=self.timeout,
					xonxoff=False,          # Kein Software-Flow-Control
					rtscts=False,           # Kein Hardware-Flow-Control (DTR/CTS)
					dsrdtr=False
				)

				logger.info(f"NFC Reader verbunden an {self.port} @ {self.baudrate} Baud")
				self.wakeup_and_arm_reader()
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
							baudrate=self.baudrate,        # Standard-Baudrate laut Handbuch
							bytesize=serial.EIGHTBITS,
							parity=serial.PARITY_NONE,
							stopbits=serial.STOPBITS_ONE,
							timeout=self.timeout,
							xonxoff=False,          # Kein Software-Flow-Control
							rtscts=False,           # Kein Hardware-Flow-Control (DTR/CTS)
							dsrdtr=False
						)
						self.wakeup_and_arm_reader()
					except serial.SerialException as e:
						logger.error(f"Device {self.name} Error(R1): " + str(e))
						time.sleep(2)
						continue

				data_bytes = self.serial.readline()
				if not data_bytes:
					continue

				data = self.parse_rfid_response(data_bytes.hex())

				try:
					logger.info(f"Device {self.name} RX: {data_bytes.hex().upper()}  => UUID: {data}")
					if(data != None):
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


	def wakeup_and_arm_reader(self):
		"""
		Initialisiert den Reader vollständig:
		1. GET_INFO (Weckt den Kommunikationsstack)
		2. PCD_TYPEA_INIT (Aktiviert das 13.56 MHz Feld)
		3. SET RUNNING MODE (Startet das automatische Polling)
		"""
		# Die Adresse aus deiner Geräte-Config (netAdr: 1)
		addr = 0x01
		
		def send_internal_cmd(cmd_byte, data=[]):
			# Frame-Struktur: SOH, ADDR, LEN_MSB, LEN_LSB, CMD, DATA..., BCC
			length = len(data) + 1
			msg = [0x01, addr, (length >> 8) & 0xFF, length & 0xFF, cmd_byte] + data
			
			# BCC berechnen (XOR über alle Bytes im Paket)
			bcc = 0
			for b in msg:
				bcc ^= b
			msg.append(bcc)
			
			self.serial.write(bytes(msg))
			time.sleep(0.15) # Dem Reader Zeit zum Verarbeiten geben
			
			if self.serial.in_waiting > 0:
				return self.serial.read(self.serial.in_waiting)
			return None

		logging.info("Sende Wakeup-Sequenz an Reader...")

		# Schritt 1: GET_INFO (Index 00) - Der "Ping"
		# SOH(01) ADDR(01) LEN(0001) CMD(72) DATA(00) BCC(73)
		res_info = send_internal_cmd(0x72, [0x00])
		if res_info:
			logging.info(f"Reader gefunden: {res_info.hex()}")
		else:
			logging.warning("Keine Antwort auf GET_INFO (Reader evtl. schon wach?)")

		# Schritt 2: PCD_TYPEA_INIT - Antenne einschalten
		# SOH(01) ADDR(01) LEN(0001) CMD(20) BCC(21)
		res_init = send_internal_cmd(0x20)
		logging.info("Antennenfeld aktiviert.")

		# Schritt 3: SET RUNNING MODE (Mode 1 = Polling / Automatik)
		# SOH(01) ADDR(01) LEN(0001) CMD(5D) DATA(01) BCC(5D)
		res_mode = send_internal_cmd(0x5D, [0x01])
		
		if res_mode and res_mode[4] == 0x00: # Status Byte prüfen
			logging.info("Erfolg: Reader ist jetzt im automatischen Event-Modus.")
		else:
			logging.error("Fehler beim Setzen des Polling-Modus.")

		# Puffer leeren, damit nur noch neue Karten-Events kommen
		self.serial.reset_input_buffer()
	
	def parse_rfid_response(self, data_hex):
		# In Bytes umwandeln falls es ein String ist
		raw = bytes.fromhex(data_hex)
		
		if raw[0] != 0x01:
			logging.error('Ungültiger Header')
			return None
		
		length = (raw[2] << 8) + raw[3]
		payload = raw[4:4+length]
		bcc_received = raw[-1]
		
		# BCC Validierung (XOR über alles vor dem BCC)
		bcc_calc = 0
		for b in raw[:-1]:
			bcc_calc ^= b
			
		if bcc_calc != bcc_received:
			logging.error("BCC Fehler (Daten korrupt)")
			return None
		
		
		if payload[0] != 0x31: # Event PICC_ACK
			logging.error("KEIN NFC EVENT")
			return None

		# Wenn du weißt, dass du 7-Byte Karten nutzt:
		uid_len = 7 
		
		# Alternativ: Dynamisch prüfen, ob das 7-Byte Flag im tag_info (0x74) steckt
		# Bei 0x74 ist oft Bit 6 oder 4 der Indikator für 7 Bytes
		if (payload[1] & 0x70) == 0x70: 
			uid_len = 7
		else:
			uid_len = 4

		uid = payload[2:2+uid_len]
		return uid.hex().upper()

	# ###########################################################
	# ###########################################################
	# ###########################################################
	# ###########################################################

	def extract_uidN(hex_string):
		try:
			data = bytes.fromhex(hex_string)
			if len(data) < 7:
				print("Datensatz zu kurz für gültiges Event.")
				return None

			offset = 4 if data[0] == 0x01 else 0
			event_code = data[offset]

			if event_code != 0x31:
				print(f"Kein PICC_ACK Event (Code: {hex(event_code)})")
				return None

			tag_info = data[offset + 1]
			taginfo_uid_map = {
				0x40: 4,
				0x44: 7,
				0x48: 4,
				0x68: 7,
				0x6C: 7,
				0x74: 7,
				0x78: 10
			}

			uid_len = taginfo_uid_map.get(tag_info, 0)
			if uid_len == 0:
				print(f"Unbekannter TagInfo-Wert: {hex(tag_info)}")
				return None

			uid_start = offset + 2
			uid_end = uid_start + uid_len
			if len(data) < uid_end:
				print("Datensatz zu kurz für vollständige UID.")
				return None

			uid_bytes = data[uid_start:uid_end]
			uid_hex = uid_bytes.hex().upper()
			return uid_hex

		except Exception as e:
			print(f"Fehler beim Parsen: {e}")
			return None
	
	def extract_uid(hex_string):
		try:
			data = bytes.fromhex(hex_string)

			# --- HEADER-SYNCHRONISIERUNG ---
			start_index = data.find(b'\x01\x01')
			if start_index == -1:
				print("Kein gültiger Header (0101) gefunden.")
				return ''
			# Daten ab Header
			data = data[start_index:]

			# Mindestlänge prüfen
			if len(data) < 7:
				print("Datensatz zu kurz für gültiges Event.")
				return ''

			# Event-Code prüfen (0x31 = PICC_ACK)
			event_code = data[4]
			if event_code != 0x31:
				print(f"Kein PICC_ACK Event (Code: {hex(event_code)})")
				return ''

			# TagInfo-Byte auslesen
			tag_info = data[5]

			# Bekannte TagInfo-Werte direkt zuordnen
			taginfo_uid_map = {
				0x40: 4,  # Mifare Classic
				0x44: 7,  # Mifare Ultralight
				0x48: 4,  # Mifare DESFire
				0x68: 7,  # NTAG
				0x6C: 7,  # ICODE
				0x74: 7,  # DESFire EV1
				0x78: 10  # ISO14443-4 Extended UID
			}

			uid_len = taginfo_uid_map.get(tag_info, 0)
			if uid_len == 0:
				print(f"Unbekannter TagInfo-Wert: {hex(tag_info)}")
				return ''

			# UID extrahieren
			uid_start = 6
			uid_end = uid_start + uid_len
			if len(data) < uid_end:
				print("Datensatz zu kurz für vollständige UID.")
				return ''

			uid_bytes = data[uid_start:uid_end]
			uid_hex = uid_bytes.hex().upper()
			return uid_hex

		except Exception as e:
			print(f"Fehler beim Parsen: {e}")
			return ''
