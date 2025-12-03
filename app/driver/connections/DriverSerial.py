from app.driver.connections.driver_connection import DriverConnection

class DriverSerial(DriverConnection):

    def __init__(self,port,baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.thread = None