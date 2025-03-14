from dataclasses import dataclass

from app.echonet.classcode import ClassCode, ClassGroupCode


@dataclass
class EOJ:
    """ECHONET オブジェクト（EOJ）"""

    @dataclass
    class EnetObj:
        classGroupCode: ClassGroupCode
        """クラスグループコード"""
        classCode: ClassCode
        """クラスコード"""
        instanceCode: int
        """インスタンスコード"""

    src: EnetObj
    """送信元ECHONET Liteオブジェクト指定"""
    dst: EnetObj
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
    def decode(cls, data: bytes) -> "EOJ":
        return EOJ(
            src=cls.decode_single(data[0:3]),
            dst=cls.decode_single(data[3:6]),
        )

    @classmethod
    def decode_single(cls, data: bytes) -> "EOJ.EnetObj":
        return EOJ.EnetObj(
            classGroupCode=ClassGroupCode(int(data[0])),
            classCode=ClassCode(int(data[1])),
            instanceCode=int(data[2]),
        )
