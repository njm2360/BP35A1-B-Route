from dataclasses import dataclass

from app.echonet.classcode import ClassCode, ClassGroupCode


@dataclass
class EnetObject:
    classGroupCode: ClassGroupCode
    """クラスグループコード"""
    classCode: ClassCode
    """クラスコード"""
    instanceCode: int
    """インスタンスコード"""


@dataclass
class EnetObjectHeader:
    """ECHONET オブジェクト（EOJ）"""

    src: EnetObject
    """送信元ECHONET Liteオブジェクト指定"""
    dst: EnetObject
    """相手先ECHONET Liteオブジェクト指定 """

    def encode(self) -> list[int]:
        return [
            int(self.src.classGroupCode),
            int(self.src.classCode),
            self.src.instanceCode,
            int(self.dst.classGroupCode),
            int(self.dst.classCode),
            self.dst.instanceCode,
        ]

    @classmethod
    def decode(cls, data: bytes) -> "EnetObjectHeader":
        if len(data) != 6:
            raise ValueError(f"Invalid data length: expected 6 bytes, got {len(data)}")
        return EnetObjectHeader(
            src=cls.decode_enet_obj(data[0:3]),
            dst=cls.decode_enet_obj(data[3:6]),
        )

    @classmethod
    def decode_enet_obj(cls, data: bytes) -> "EnetObject.EnetObj":
        if len(data) != 3:
            raise ValueError(f"Invalid data length: expected 3 bytes, got {len(data)}")
        return EnetObject(
            classGroupCode=ClassGroupCode(int(data[0])),
            classCode=ClassCode(int(data[1])),
            instanceCode=int(data[2]),
        )
