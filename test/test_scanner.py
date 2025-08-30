import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.devices.data_scanner import DataScanner

scanner =  DataScanner(port="COM3")
scanner.listen()