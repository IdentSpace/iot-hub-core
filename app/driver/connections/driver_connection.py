from abc import ABC, abstractmethod

class DriverConnection(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def listen(self):
        pass

    @abstractmethod
    def listen_in_thread(self):
        pass