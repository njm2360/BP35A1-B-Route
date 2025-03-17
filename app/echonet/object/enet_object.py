from dataclasses import dataclass
from app.echonet.object.classcode import ClassCode, ClassGroupCode


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
