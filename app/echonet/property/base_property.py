from enum import IntEnum
from dataclasses import dataclass
from typing import Optional, Union
from datetime import date, datetime, time

from app.echonet.property.install_location import LocationCode, SpecialLocationCode
from app.echonet.property.property import Property
from app.echonet.protocol.access import Access


@dataclass
class OpStatus(Property):
    """動作状態(0x80)"""

    status: bool = False
    """状態"""

    def __post_init__(self):
        self.code = 0x80
        self.accessRules = [Access.GET, Access.SET]

    @classmethod
    def decode(cls, data: bytes):
        return cls(status=data[0] == 0x30)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            result.append(0x01)
            result.append(0x30 if self.status else 0x31)

        return result


@dataclass
class InstallLocation(Property):
    """設置場所プロパティ(0x81)"""

    location_code: Union[LocationCode, SpecialLocationCode] = (
        SpecialLocationCode.NOT_SET
    )
    location_number: int = 0
    free_defined: bool = False
    position_information: Optional[bytes] = None

    def __post_init__(self):
        self.code = 0x81
        self.accessRules = [Access.GET, Access.SET]

        if isinstance(self.location_code, SpecialLocationCode):
            self._location = self.location_code.value
            if self.location_code == SpecialLocationCode.POSITION_INFORMATION:
                if (
                    self.position_information is None
                    or len(self.position_information) != 16
                ):
                    raise ValueError(
                        "position_information must be 16 bytes for POSITION_INFORMATION"
                    )
        else:
            if not 0 <= self.location_number < 8:
                raise ValueError("location_number must be 0 between 7.")

            if self.free_defined:
                self._location = (
                    0b10000000 | (self.location_code.value << 3) | self.location_number
                )
            else:
                self._location = (self.location_code.value << 3) | self.location_number

    @classmethod
    def decode(cls, data: bytes):
        location = data[0]
        if location == SpecialLocationCode.POSITION_INFORMATION:
            position_information = data[1:17]
            return cls(
                location_code=SpecialLocationCode.POSITION_INFORMATION,
                position_information=position_information,
            )
        elif location in SpecialLocationCode._value2member_map_:
            return cls(location_code=SpecialLocationCode(location))
        else:
            free_defined = (location & 0b10000000) != 0
            code = (location & 0b01111000) >> 3
            location_number = location & 0b00000111
            return cls(
                location_code=LocationCode(code),
                location_number=location_number,
                free_defined=free_defined,
            )

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            if (
                self.location_code == SpecialLocationCode.POSITION_INFORMATION
                and self.position_information
            ):
                result.append(0x11)
                result.append(self.location_code.value)
                result.extend(self.position_information)
            else:
                result.append(0x01)
                result.append(self._location & 0xFF)

        return result


@dataclass
class VersionInfo(Property):
    """規格Version情報(0x82)"""

    release: str = ""
    """リリース"""
    rev_no: int = 0
    """リビジョン番号"""

    def __post_init__(self):
        self.code = 0x82
        self.accessRules = [Access.GET]

    @classmethod
    def decode(cls, data: bytes):
        release = chr(data[2])
        rev_no = data[3]
        return cls(release, rev_no)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            raise NotImplementedError()

        return result


@dataclass
class IdentifierNo(Property):
    """識別番号(0x83)"""

    # low_layer_id: int = 0
    # """下位通信層ID"""

    def __post_init__(self):
        self.code = 0x83
        self.accessRules = [Access.GET]

    @classmethod
    def decode(cls, data: bytes):
        raise NotImplementedError()

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            raise NotImplementedError()

        return result


@dataclass
class InstantPowerConsumption(Property):
    """瞬時消費電力計測値(0x84)"""

    value: int = 0
    """計測値(W)"""

    def __post_init__(self):
        self.code = 0x84
        self.accessRules = [Access.GET]

    @classmethod
    def decode(cls, data: bytes):
        value = int.from_bytes(data, byteorder="big")
        return cls(value)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            raise NotImplementedError()

        return result


@dataclass
class CumulativePowerConsumption(Property):
    """積算消費電力量計測値(0x85)"""

    value: float = 0
    """計測値(kWh)"""

    def __post_init__(self):
        self.code = 0x85
        self.accessRules = [Access.GET]

    @classmethod
    def decode(cls, data: bytes):
        value = int.from_bytes(data, byteorder="big") / 1000
        return cls(value)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            raise NotImplementedError()

        return result


@dataclass
class ManufacturerErrorCode(Property):
    """メーカ異常コード(0x86)"""

    size: int = 0
    """異常コード部のデータサイズ"""
    manufactor_code: int = 0
    """メーカーコード"""
    error_code: bytes = b""
    """異常コード部"""

    def __post_init__(self):
        self.code = 0x86
        self.accessRules = [Access.GET]

    @classmethod
    def decode(cls, data: bytes):
        size = data[0]
        manufactor_code = int.from_bytes(data[1:4], byteorder="big")
        error_code = data[4:]
        return cls(size, manufactor_code, error_code)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            raise NotImplementedError()

        return result


@dataclass
class CurrentLimitSetting(Property):
    """電流制限設定(0x87)"""

    value: int = 0
    """設定値(%)"""

    def __post_init__(self):
        self.code = 0x87
        self.accessRules = [Access.GET]

    @classmethod
    def decode(cls, data: bytes):
        value = data[0]
        return cls(value)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            raise NotImplementedError()

        return result


@dataclass
class AbnormalState(Property):
    """異常発生状態(0x88)"""

    status: bool = False
    """異常状態"""

    def __post_init__(self):
        self.code = 0x88
        self.accessRules = [Access.GET]

    @classmethod
    def decode(cls, data: bytes):
        status = data[0] == 0x41
        return cls(status)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            raise NotImplementedError()

        return result


@dataclass
class MemberID(Property):
    """会員ID／メーカコード(0x8A)"""

    manufactor_code: int = 0
    """コード"""

    def __post_init__(self):
        self.code = 0x8A
        self.accessRules = [Access.GET]

    @classmethod
    def decode(cls, data: bytes):
        manufactor_code = int.from_bytes(data, byteorder="big")
        return cls(manufactor_code)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            raise NotImplementedError()

        return result


@dataclass
class BusinessCode(Property):
    """事業場コード(0x8B)"""

    business_code: int = 0
    """コード"""

    def __post_init__(self):
        self.code = 0x8B
        self.accessRules = [Access.GET]

    @classmethod
    def decode(cls, data: bytes):
        business_code = int.from_bytes(data, byteorder="big")
        return cls(business_code)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            raise NotImplementedError()

        return result


@dataclass
class ProductCode(Property):
    """商品コード(0x8C)"""

    product_code: str = ""
    """コード"""

    def __post_init__(self):
        self.code = 0x8C
        self.accessRules = [Access.GET]

    @classmethod
    def decode(cls, data: bytes):
        product_code = data.decode()
        return cls(product_code)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            raise NotImplementedError()

        return result


@dataclass
class SerialNumber(Property):
    """製造番号(0x8D)"""

    value: str = ""
    """コード"""

    def __post_init__(self):
        self.code = 0x8D
        self.accessRules = [Access.GET]

    @classmethod
    def decode(cls, data: bytes):
        value = data.decode()
        return cls(value)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            raise NotImplementedError()

        return result


@dataclass
class ManufactureDate(Property):
    """製造年月日(0x8E)"""

    value: datetime = None
    """製造年月日"""

    def __post_init__(self):
        self.code = 0x8E
        self.accessRules = [Access.GET]

    @classmethod
    def decode(cls, data: bytes):
        year = int.from_bytes(data[0:2], byteorder="big")
        month = data[2]
        day = data[3]
        return cls(value=datetime(year, month, day))

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            raise NotImplementedError()

        return result


@dataclass
class PowerSavingMode(Property):
    """節電動作設定(0x8F)"""

    class State(IntEnum):
        POWER_SAVE_OP = 0x41  # 節電動作中
        NORMAL_OP = 0x42  # 通常動作中

    state: State = None
    """状態"""

    def __post_init__(self):
        self.code = 0x8F
        self.accessRules = [Access.GET, Access.SET]

    @classmethod
    def decode(cls, data: bytes):
        state = cls.State(data[0])
        return cls(state)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            result.append(0x01)
            result.append(self.state.value)

        return result


@dataclass
class RemoteControlSetting(Property):
    """遠隔操作設定(0x93)"""

    class State(IntEnum):
        PUBLIC_LINE_UNUSED = 0x41  # 公衆回線未経由操作
        PUBLIC_LINE_USED = 0x42  # 公衆回線経由操作
        LINE_NORMAL_NO_PUBLIC = 0x61  # 通信回線正常（公衆回線経由の操作不可）
        LINE_NORMAL_WITH_PUBLIC = 0x62  # 通信回線正常（公衆回線経由の操作可能）

    state: State = None
    """状態"""

    def __post_init__(self):
        self.code = 0x93
        self.accessRules = [Access.GET, Access.SET]

    @classmethod
    def decode(cls, data: bytes):
        state = cls.State(data[0])
        return cls(state)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            result.append(0x01)
            result.append(self.state.value)

        return result


@dataclass
class CurrentTime(Property):
    """現在時刻設定(0x97)"""

    value: time = None
    """値"""

    def __post_init__(self):
        self.code = 0x97
        self.accessRules = [Access.GET, Access.SET]

    @classmethod
    def decode(cls, data: bytes):
        value = time(data[0], data[1])
        return cls(value)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            result.append(0x02)
            result.append(self.value.hour)
            result.append(self.value.minute)

        return result


@dataclass
class CurrentDate(Property):
    """現在年月日設定(0x98)"""

    value: date = None
    """値"""

    def __post_init__(self):
        self.code = 0x98
        self.accessRules = [Access.GET, Access.SET]

    @classmethod
    def decode(cls, data: bytes):
        value = date(int.from_bytes(data[0:2], byteorder="big"), data[2], data[3])
        return cls(value)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            result.append(0x04)
            result.extend(self.value.year.to_bytes(2, byteorder="big"))
            result.append(self.value.month)
            result.append(self.value.day)

        return result


@dataclass
class PowerLimitSetting(Property):
    """電力制限設定(0x99)"""

    value: int = 0
    """制限値(W)"""

    def __post_init__(self):
        self.code = 0x99
        self.accessRules = [Access.GET, Access.SET]

    @classmethod
    def decode(cls, data: bytes):
        value = int.from_bytes(data, byteorder="big")
        return cls(value)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            result.append(0x02)
            result.extend(self.value.to_bytes(2, byteorder="big"))

        return result


@dataclass
class CumulativeOperatingTime(Property):
    """積算運転時間(0x9A)"""

    class Unit(IntEnum):
        SECOND = 0x41
        MINUTE = 0x42
        HOUR = 0x43
        DAY = 0x44

    unit: Unit = None
    """単位"""
    value: int = 0
    """積算運転時間"""

    def __post_init__(self):
        self.code = 0x9A
        self.accessRules = [Access.GET]

    @classmethod
    def decode(cls, data: bytes):
        unit = cls.Unit(data[0])
        value = int.from_bytes(data[1:5], byteorder="big")
        return cls(unit, value)

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = [self.code]

        if mode == Access.GET:
            result.append(0x00)
        else:
            raise NotImplementedError()

        return result
