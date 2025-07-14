import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.devices.nfc_reader import NfcReader



NfcReader().listen()