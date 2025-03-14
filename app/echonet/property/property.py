from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.echonet.protocol.access import Access


@dataclass
class Property(ABC):
    code: int = field(init=False, repr=False)
    """EPCコード"""
    accessRules: list[Access] = field(init=False, repr=False)
    """アクセスルール"""

    @abstractmethod
    def decode(self, data: bytes):
        pass

    @abstractmethod
    def encode(self, mode: Access) -> list[int]:
        pass
