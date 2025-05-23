from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.echonet.object.access import Access


@dataclass
class Property(ABC):
    code: int = field(init=False, repr=False)
    """EPCコード"""
    access_rules: list[Access] = field(init=False, repr=False)
    """アクセスルール"""

    @abstractmethod
    def decode(self, data: bytes):
        """デコード(EDTのみ)"""
        pass

    @abstractmethod
    def encode(self) -> bytes:
        """エンコード(EDTのみ)"""
        pass
