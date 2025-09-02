from app.driver.types.parking_barrier import ParkingBarrier
from app.driver.types.device import DeviceBase, DeviceState
from abc import ABC
import xmlrpc.client

class AS1620(DeviceBase, ParkingBarrier):

    def __init__(self, ip:str, port:int):
        self.URI = "http://{0}:{1}".format(ip,port)
        self.proxy = xmlrpc.client.ServerProxy(self.URI)

    def open_tree(self):
        print("Parking Barrier open")

        try:
            result = self.proxy.SetOpen()
            # TODO: validate result
            return True
        except Exception as e:
            print("FEHLER")
            return False

    def close_tree(self):
        print("Parking Barrier Close")

        try:
            result = self.proxy.SetClose()
            # TODO: validate result
            return True
        except Exception as e:
            print("FEHLER")
            return False
        
    def get_state(self):
        return DeviceState(state=DeviceState.NONE, message="NOT IMPLEMENTED", raw_data={})
    