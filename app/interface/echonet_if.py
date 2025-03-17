from abc import ABC, abstractmethod


class EchonetInterface(ABC):
    @property
    @abstractmethod
    def packet_size_limit(self) -> int:
        pass

    @abstractmethod
    async def send_data(self, data: bytes):
        pass

    @abstractmethod
    async def get_data(self) -> bytes:
        pass
