from dataclasses import dataclass
from app.echonet.classcode import ClassCode, ClassGroupCode


@dataclass
class EnetObject:
    """ECHONET Lite オブジェクト（EOJ）"""

    classGroupCode: ClassGroupCode
    """クラスグループコード"""
    classCode: ClassCode
    """クラスコード"""
    instanceCode: int
    """インスタンスコード"""

    def encode(self) -> list[int]:
        return [int(self.classGroupCode), int(self.classCode), self.instanceCode]

    @classmethod
    def decode(cls, data: bytes) -> "EnetObject":
        if len(data) != 3:
            raise ValueError(f"Invalid data length: expected 3 bytes, got {len(data)}")
        return cls(
            classGroupCode=ClassGroupCode(int(data[0])),
            classCode=ClassCode(int(data[1])),
            instanceCode=int(data[2]),
        )


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
