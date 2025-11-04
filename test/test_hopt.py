# import serial; s=serial.Serial('COM11',115200,timeout=1); s.write(b'\x01\x01\x00\x01\x33\x32'); s.close()
# import serial; s=serial.Serial('COM11',115200,timeout=1); s.write(b'\x01\x01\x00\x02\x4D\x00\x4C'); s.close()
# import serial; s=serial.Serial('COM11', 115200, timeout=1); s.write(b'\x01\x01\x00\x03\x4C\x03\x01\x4B'); s.close()
import serial

payload = [
    0x01,       # Baudrate-Code: 38400 → 0x02 (je nach Mapping)
    0x01,       # Adresse
    0x01,       # Display-Modus
    0x01,       # Polling aktiv
    0x00        # UID-Format: HEX
]

def xor_checksum(data):
    bcc = 0
    for b in data:
        bcc ^= b
    return bcc

def build_memory_write_frame(addr=0x01, file_id=0x00, payload=None):
    if payload is None:
        payload = [0x02, 0x01, 0x01, 0x01, 0x00]  # Beispielwerte
    SOH = 0x01
    cmd = 0x4A
    length = len(payload) + 2  # CMD + FileID + Payload
    len_msb = (length >> 8) & 0xFF
    len_lsb = length & 0xFF
    frame = [SOH, addr, len_msb, len_lsb, cmd, file_id] + payload
    frame.append(xor_checksum(frame))
    return bytes(frame)


def send_memory_write(port="COM11", baudrate=115200):
    frame = build_memory_write_frame()
    print(f"📤 Sende MEMORY_WRITE mit Default-Konfig")
    print(f"🔧 Frame: {' '.join(f'{b:02X}' for b in frame)}")
    with serial.Serial(port=port, baudrate=baudrate, timeout=2) as ser:
        ser.write(frame)
        response = ser.read(64)
        print(f"✅ Antwort: {response.hex().upper()}")

send_memory_write()

# COMFIG AUSLESEN

with serial.Serial('COM11', 115200, timeout=3) as ser:
    ser.write(b'\x01\x01\x00\x02\x4B\x00\x48')  # MEMORY_READ
    response = ser.read(128)
    print(f"Antwort: {response.hex().upper()}")
exit()

import serial

def xor_checksum(data):
    """Berechnet den XOR (BCC) über alle Bytes."""
    bcc = 0
    for b in data:
        bcc ^= b
    return bcc

def build_memory_erase_frame(addr=0x01):
    """Erstellt den Frame für MEMORY_ERASE mit FileID 0x00."""
    SOH = 0x01
    length = [0x00, 0x02]  # 2 Bytes: Command + Parameter
    command = 0x4D         # MEMORY_ERASE
    file_id = 0x00         # config.json
    frame = [SOH, addr] + length + [command, file_id]
    frame.append(xor_checksum(frame))
    return bytes(frame)

def send_memory_erase(port="COM11", baudrate=115200):
    frame = build_memory_erase_frame()
    print(f"📤 Sende MEMORY_ERASE an {port} @ {baudrate} Baud")
    print(f"🔧 Frame: {' '.join(f'{b:02X}' for b in frame)}")
    try:
        with serial.Serial(port=port, baudrate=baudrate, timeout=2) as ser:
            ser.write(frame)
            response = ser.read(64)
            if response:
                print(f"✅ Antwort erhalten: {response.hex().upper()}")
            else:
                print("❌ Keine Antwort vom Gerät")
    except Exception as e:
        print(f"⚠️ Fehler: {e}")

def build_get_info_frame(addr=0x01):
    frame = [0x01, addr, 0x00, 0x01, 0x72]
    frame.append(xor_checksum(frame))
    return bytes(frame)

def send_get_info(port="COM11", baudrate=38400):
    frame = build_get_info_frame()
    print(f"📤 Sende GET_INFO an {port} @ {baudrate} Baud")
    print(f"🔧 Frame: {' '.join(f'{b:02X}' for b in frame)}")
    try:
        with serial.Serial(port=port, baudrate=baudrate, timeout=2) as ser:
            ser.write(frame)
            response = ser.read(64)
            if response:
                print(f"✅ Antwort erhalten: {response.hex().upper()}")
            else:
                print("❌ Keine Antwort vom Gerät")
    except Exception as e:
        print(f"⚠️ Fehler: {e}")

def build_set_baudrate_frame(addr=0x01, baud_code=0x02):
    # SET_CONFIG (0x4C), Param: Baudrate (0x01), Value: baud_code
    frame = [0x01, addr, 0x00, 0x03, 0x4C, 0x01, baud_code]
    frame.append(xor_checksum(frame))
    return bytes(frame)

def send_set_baudrate(port="COM11", current_baud=115200, target_code=0x02):
    frame = build_set_baudrate_frame(baud_code=target_code)
    print(f"📤 Sende SET_CONFIG (Baudrate) an {port} @ {current_baud} Baud")
    print(f"🔧 Frame: {' '.join(f'{b:02X}' for b in frame)}")
    try:
        with serial.Serial(port=port, baudrate=current_baud, timeout=2) as ser:
            ser.write(frame)
            response = ser.read(64)
            if response:
                print(f"✅ Antwort erhalten: {response.hex().upper()}")
            else:
                print("❌ Keine Antwort vom Gerät")
    except Exception as e:
        print(f"⚠️ Fehler: {e}")

if __name__ == "__main__":
    # send_memory_erase()
    # send_get_info()
    send_set_baudrate(target_code=0x04)  # 0x02 = 38400 Baud