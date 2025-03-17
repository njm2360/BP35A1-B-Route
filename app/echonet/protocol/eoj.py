from dataclasses import dataclass
from app.echonet.object.enet_object import EnetObject


@dataclass
class EnetObjectHeader:
    """ECHONET Lite オブジェクトヘッダー（EHD）"""

    src: EnetObject
    """送信元 ECHONET Lite オブジェクト"""
    dst: EnetObject
    """宛先 ECHONET Lite オブジェクト"""

    def encode(self) -> list[int]:
        return self.src.encode() + self.dst.encode()

    @classmethod
    def decode(cls, data: bytes) -> "EnetObjectHeader":
        if len(data) != 6:
            raise ValueError(f"Invalid data length: expected 6 bytes, got {len(data)}")
        return cls(
            src=EnetObject.decode(data[0:3]),
            dst=EnetObject.decode(data[3:6]),
        )
