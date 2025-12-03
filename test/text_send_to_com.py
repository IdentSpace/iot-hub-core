import serial
import time

# COM-Port des virtuellen Lesegeräts
ser = serial.Serial('COM7', 115200, timeout=1)

# Beispiel-Paket (wie oben)
hex_string = "34343434301010012317404330a8aa65880440320067577810280fe"
data = bytes.fromhex(hex_string)

while True:
    ser.write(data)   # Paket senden
    time.sleep(4)     # alle 2 Sekunden senden