import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.driver.default_data_scanner import DefaultDataScanner

scanner = DefaultDataScanner(port="COM3")
print(scanner.list_bases())

scanner.listen()