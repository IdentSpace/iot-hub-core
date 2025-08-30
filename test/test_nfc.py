# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from app.devices.nfc_reader import NfcReader



# NfcReader().listen()


import socket
import time


def poll_uid(ip="192.168.51.160", port=6001, dev_id="MCRN2P-552D"):
    while True:
        try:
            # Verbindung aufbauen
            with socket.create_connection((ip, port), timeout=5) as s:
                command = f"{dev_id},GETUID\n"
                s.sendall(command.encode("utf-8"))

                # Antwort lesen
                response = s.recv(1024).decode("utf-8").strip()
                if "UID=" in response:
                    uid = response.split("UID=")[1]
                    print(f"UID: {uid}")
                else:
                    print("Keine UID erkannt")

        except Exception as e:
            print(f"Fehler: {e}")

        # 1 Sekunde warten, dann wiederholen
        time.sleep(1)


if __name__ == "__main__":
    poll_uid()