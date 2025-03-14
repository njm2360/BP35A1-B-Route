from datetime import datetime
from dataclasses import dataclass

from app.echonet.property.base_property import Property
from app.echonet.protocol.access import Access


@dataclass
class MomentPower(Property):
    """瞬時電力計測値(0xE7)"""

    value: int = None
    """計測値(W)"""

    def __post_init__(self):
        self.code = 0xE7
        self.accessRules = [Access.GET]

    @classmethod
    def decode(cls, data: bytes) -> "MomentPower":
        return cls(value=int.from_bytes(data[:4], byteorder="big"))

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            result.append(0x04)
            result.extend(self.value.to_bytes(4, byteorder="big"))

        return result


@dataclass
class MomentCurrent(Property):
    """瞬時電流計測値(0xE8)"""

    rPhase: float = None
    """R相電流"""
    tPhase: float = None
    """T相電流"""

    def __post_init__(self):
        self.code = 0xE8
        self.accessRules = [Access.GET]

    @classmethod
    def decode(cls, data: bytes) -> "MomentCurrent":
        rPhase = int.from_bytes(data[0:2], byteorder="big") / 10
        tPhase = int.from_bytes(data[2:4], byteorder="big") / 10

        return cls(rPhase, tPhase)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            result.append(0x04)
            result.extend(int(self.rPhase * 10).to_bytes(2, byteorder="big"))
            result.extend(int(self.tPhase * 10).to_bytes(2, byteorder="big"))

        return result


@dataclass
class CumulativePowerMeasurement(Property):
    timestamp: datetime
    """タイムスタンプ"""
    value: int
    """積算電力量"""

    @classmethod
    def decode(cls, data: bytes) -> "CumulativePowerMeasurement":
        year = int.from_bytes(data[0:2], byteorder="big")
        month = data[2]
        day = data[3]
        hour = data[4]
        minute = data[5]
        second = data[6]
        power = int.from_bytes(data[7:11], byteorder="big")

        timestamp = datetime(year, month, day, hour, minute, second)
        return cls(timestamp, power)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            result.append(0x0B)
            result.extend(self.timestamp.year.to_bytes(2, byteorder="big"))
            result.append(self.timestamp.month)
            result.append(self.timestamp.day)
            result.append(self.timestamp.hour)
            result.append(self.timestamp.minute)
            result.append(self.timestamp.second)
            result.extend(self.value.to_bytes(4, byteorder="big"))

        return result


@dataclass
class CumulativeEnergyNormalDir(CumulativePowerMeasurement):
    """定時積算電力量計測値(正方向計測値) (0xEA)"""

    def __post_init__(self):
        self.code = 0xEA
        self.accessRules = [Access.GET]


@dataclass
class CumulativeEnergyReverseDir(CumulativePowerMeasurement):
    """定時積算電力量計測値（逆方向計測値） (0xEB)"""

    def __post_init__(self):
        self.code = 0xEB
        self.accessRules = [Access.GET]
