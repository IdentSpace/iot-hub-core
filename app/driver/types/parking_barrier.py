from abc import ABC, abstractmethod

class ParkingBarrier(ABC):
    @abstractmethod
    def open_tree(self)->bool:
        pass

    @abstractmethod
    def close_tree(self)->bool:
        pass