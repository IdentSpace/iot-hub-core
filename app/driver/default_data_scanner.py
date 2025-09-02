from app.driver.types.data_scanner import DataScanner, Parser, DataScannerData
from app.driver.types.device import DeviceBase, DeviceState
from app.state.dscanner import set_latest_dscanner_data
import serial
import threading

class DefaultDataScanner(DeviceBase, DataScanner):

    def __init__(self,port:str,baudrate=9600,timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.thread = None
        self.serial = None

    def listen(self):
        self.serial = serial.Serial(port=self.port,baudrate=self.baudrate,timeout=self.timeout)

        while True:
            if self.serial.in_waiting > 0:
                try:
                    data = self.serial.readline().decode('utf-8').strip()
                    if data:
                        print(f"Received data: {data}")
                        gs1DM = Parser.gs1_datamatrix(data)
                        if(gs1DM["success"] == True):
                            set_latest_dscanner_data(DataScannerData(type="datamatrix_gs1",data=data))
                        else:
                            set_latest_dscanner_data(DataScannerData(type="raw",data=data))
                except Exception as e:
                    print("Error")

    def listen_in_thread(self):
        self.thread = threading.Thread(target=self.listen)
        self.thread.daemon = True
        self.thread.start()
        return self

    def close(self):
        if self.serial.is_open:
            self.serial.close()
        if self.thread:
            self.thread.join()

    def get_state(self):
        return DeviceState(state=DeviceState.NONE, message="NOT IMPLEMENTED", raw_data={})
    
    def raw_command(self):
        return super().raw_command()