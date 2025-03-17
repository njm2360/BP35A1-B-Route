import struct
from enum import IntEnum
from typing import Optional, Union
from dataclasses import dataclass, field
from datetime import date, datetime, time

from app.echonet.object.access import Access
from app.echonet.property.property import Property
from app.echonet.property.install_location import LocationCode, SpecialLocationCode


class BaseProperty:
    @dataclass
    class OpStatus(Property):
        """動作状態(0x80)"""

        status: bool = True
        """状態"""

        def __post_init__(self):
            self.code = 0x80
            self.access_rules = [Access.GET, Access.SET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.OpStatus":
            if len(data) != 1:
                raise ValueError(
                    f"Invalid data length: expected 1 byte, got {len(data)}"
                )
            return cls(status=data[0] == 0x30)

        def encode(self) -> bytes:
            return struct.pack(">B", 0x30 if self.status else 0x31)

    @dataclass
    class InstallLocation(Property):
        """設置場所プロパティ(0x81)"""

        location_code: Optional[Union[LocationCode, SpecialLocationCode]] = None
        """設置場所コード"""
        location_number: Optional[int] = None
        """場所番号(0~7)"""
        free_defined: Optional[bool] = None
        """フリー定義"""
        position_information: Optional[bytes] = None
        """位置情報定義"""

        def __post_init__(self):
            self.code = 0x81
            self.access_rules = [Access.GET, Access.SET]

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
                        0b10000000
                        | (self.location_code.value << 3)
                        | self.location_number
                    )
                else:
                    self._location = (
                        self.location_code.value << 3
                    ) | self.location_number

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.InstallLocation":
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

        def encode(self) -> bytes:
            result = bytearray()

            if (
                self.location_code == SpecialLocationCode.POSITION_INFORMATION
                and self.position_information
            ):
                result.append(self.location_code.value)
                result.extend(self.position_information)
            else:
                result.append(self._location & 0xFF)

            return bytes(result)

    @dataclass
    class VersionInfo(Property):
        """規格Version情報(0x82)"""

        release: str = "A"
        """リリース"""
        rev_no: int = 0
        """リビジョン番号"""

        def __post_init__(self):
            self.code = 0x82
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.VersionInfo":
            if len(data) < 4:
                raise ValueError(
                    f"Invalid data length: expected at least 4 bytes, got {len(data)}"
                )

            release = chr(data[2])
            rev_no = data[3]

            return cls(release, rev_no)

        def encode(self) -> bytes:
            return struct.pack(">BBcB", 0, 0, self.release.encode(), self.rev_no)

    @dataclass
    class IdentifierNo(Property):
        """識別番号(0x83)"""

        # low_layer_id: int = 0
        # """下位通信層ID"""

        def __post_init__(self):
            self.code = 0x83
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes):
            raise NotImplementedError()

        def encode(self) -> bytes:
            raise NotImplementedError()

    @dataclass
    class InstantPowerConsumption(Property):
        """瞬時消費電力計測値(0x84)"""

        value: int = 0
        """計測値(W)"""

        def __post_init__(self):
            self.code = 0x84
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.InstantPowerConsumption":
            if len(data) != 4:
                raise ValueError(
                    f"Invalid data length: expected 4 bytes, got {len(data)}"
                )

            value = struct.unpack(">I", data)[0]
            return cls(value)

        def encode(self) -> bytes:
            return struct.pack(">I", self.value)

    @dataclass
    class CumulativePowerConsumption(Property):
        """積算消費電力量計測値(0x85)"""

        value: float = 0.0
        """計測値(kWh)"""

        def __post_init__(self):
            self.code = 0x85
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.CumulativePowerConsumption":
            if len(data) != 4:
                raise ValueError(
                    f"Invalid data length: expected 4 bytes, got {len(data)}"
                )

            value = struct.unpack(">I", data)[0] / 1000.0
            return cls(value)

        def encode(self) -> bytes:
            return struct.pack(">I", int(self.value * 1000))

    @dataclass
    class ManufacturerErrorCode(Property):
        """メーカ異常コード(0x86)"""

        size: Optional[int] = None
        """異常コード部のデータサイズ"""
        manufactor_code: Optional[int] = None
        """メーカーコード"""
        error_code: Optional[bytes] = None
        """異常コード部"""

        def __post_init__(self):
            self.code = 0x86
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.ManufacturerErrorCode":
            if len(data) < 4:
                raise ValueError(
                    f"Invalid data length: expected at least 4 bytes, got {len(data)}"
                )

            size = data[0]
            manufactor_code = int.from_bytes(data[1:4], byteorder="big")
            error_code = data[4:] if len(data) > 4 else None

            return cls(size, manufactor_code, error_code)

        def encode(self) -> bytes:
            size_data = struct.pack(">B", self.size if self.size is not None else 0)
            manufactor_code_data = (
                self.manufactor_code if self.manufactor_code is not None else 0
            ).to_bytes(3, byteorder="big")
            error_code_data = self.error_code if self.error_code is not None else b""
            return size_data + manufactor_code_data + error_code_data

    @dataclass
    class CurrentLimitSetting(Property):
        """電流制限設定(0x87)"""

        value: int = 100
        """設定値(%)"""

        def __post_init__(self):
            self.code = 0x87
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.CurrentLimitSetting":
            if len(data) != 1:
                raise ValueError(
                    f"Invalid data length: expected 1 byte, got {len(data)}"
                )

            value = data[0]
            return cls(value)

        def encode(self) -> bytes:
            if not (0 <= self.value <= 100):
                raise ValueError("Value must be between 0 and 100.")
            return struct.pack(">B", self.value)

    @dataclass
    class AbnormalState(Property):
        """異常発生状態(0x88)"""

        abnormal: bool = False
        """異常状態"""

        def __post_init__(self):
            self.code = 0x88
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.AbnormalState":
            if len(data) != 1:
                raise ValueError(
                    f"Invalid data length: expected 1 byte, got {len(data)}"
                )

            abnormal = data[0] == 0x41
            return cls(abnormal)

        def encode(self) -> bytes:
            return struct.pack(">B", 0x41 if self.abnormal else 0x42)

    @dataclass
    class MemberID(Property):
        """会員ID／メーカコード(0x8A)"""

        manufactor_code: int = 0xFFFFFF
        """コード"""

        def __post_init__(self):
            self.code = 0x8A
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.MemberID":
            if len(data) != 3:
                raise ValueError(
                    f"Invalid data length: expected 3 byte, got {len(data)}"
                )

            manufactor_code = int.from_bytes(data, byteorder="big")
            return cls(manufactor_code)

        def encode(self) -> bytes:
            return self.manufactor_code.to_bytes(3, byteorder="big")

    @dataclass
    class BusinessCode(Property):
        """事業場コード(0x8B)"""

        business_code: Optional[int] = None
        """コード"""

        def __post_init__(self):
            self.code = 0x8B
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.BusinessCode":
            if len(data) != 3:
                raise ValueError(
                    f"Invalid data length: expected 3 byte, got {len(data)}"
                )

            business_code = int.from_bytes(data, byteorder="big")
            return cls(business_code)

        def encode(self) -> bytes:
            return (self.business_code or 0).to_bytes(3, byteorder="big")

    @dataclass
    class ProductCode(Property):
        """商品コード(0x8C)"""

        product_code: Optional[str] = None
        """コード"""

        def __post_init__(self):
            self.code = 0x8C
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.ProductCode":
            if len(data) != 12:
                raise ValueError(
                    f"Invalid data length: expected 12 bytes, got {len(data)}"
                )

            product_code = data.decode("ascii").strip("\x00 ")
            return cls(product_code)

        def encode(self) -> bytes:
            return self.product_code.ljust(12, "\x00").encode("ascii")

    @dataclass
    class SerialNumber(Property):
        """製造番号(0x8D)"""

        value: str = ""
        """コード"""

        def __post_init__(self):
            self.code = 0x8D
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.SerialNumber":
            if len(data) != 12:
                raise ValueError(
                    f"Invalid data length: expected 12 bytes, got {len(data)}"
                )

            value = data.decode("ascii").strip("\x00 ")
            return cls(value)

        def encode(self) -> bytes:
            return self.value.ljust(12, "\x00").encode("ascii")

    @dataclass
    class ManufactureDate(Property):
        """製造年月日(0x8E)"""

        value: date = date(2000, 1, 1)
        """製造年月日"""

        def __post_init__(self):
            self.code = 0x8E
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.ManufactureDate":
            if len(data) != 4:
                raise ValueError(
                    f"Invalid data length: expected 4 bytes, got {len(data)}"
                )

            year, month, day = struct.unpack(">HBB", data)

            return cls(value=date(year, month, day))

        def encode(self) -> bytes:
            return struct.pack(
                ">HBB", self.value.year, self.value.month, self.value.day
            )

    @dataclass
    class PowerSavingMode(Property):
        """節電動作設定(0x8F)"""

        class State(IntEnum):
            POWER_SAVE_OP = 0x41  # 節電動作中
            NORMAL_OP = 0x42  # 通常動作中

        state: State = State.NORMAL_OP
        """状態"""

        def __post_init__(self):
            self.code = 0x8F
            self.access_rules = [Access.GET, Access.SET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.PowerSavingMode":
            if len(data) != 1:
                raise ValueError(
                    f"Invalid data length: expected 1 byte, got {len(data)}"
                )

            state = cls.State(data[0])
            return cls(state)

        def encode(self) -> bytes:
            return struct.pack(">B", self.state.value)

    @dataclass
    class RemoteControlSetting(Property):
        """遠隔操作設定(0x93)"""

        class State(IntEnum):
            PUBLIC_LINE_UNUSED = 0x41  # 公衆回線未経由操作
            PUBLIC_LINE_USED = 0x42  # 公衆回線経由操作
            LINE_NORMAL_NO_PUBLIC = 0x61  # 通信回線正常（公衆回線経由の操作不可）
            LINE_NORMAL_WITH_PUBLIC = 0x62  # 通信回線正常（公衆回線経由の操作可能）

        state: Optional[State] = None
        """状態"""

        def __post_init__(self):
            self.code = 0x93
            self.access_rules = [Access.GET, Access.SET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.RemoteControlSetting":
            if len(data) != 1:
                raise ValueError(
                    f"Invalid data length: expected 1 byte, got {len(data)}"
                )

            state = cls.State(data[0])
            return cls(state)

        def encode(self) -> bytes:
            if self.state is None:
                raise ValueError("State must be set before encoding for SET mode")
            return struct.pack(">B", self.state.value if self.state else 0x00)

    @dataclass
    class CurrentTime(Property):
        """現在時刻設定(0x97)"""

        value: time = time(0, 0)
        """時刻"""

        def __post_init__(self):
            self.code = 0x97
            self.access_rules = [Access.GET, Access.SET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.CurrentTime":
            if len(data) != 2:
                raise ValueError(
                    f"Invalid data length: expected 2 bytes, got {len(data)}"
                )

            value = time(data[0], data[1])
            return cls(value)

        def encode(self) -> bytes:
            return struct.pack(">BB", self.value.hour, self.value.minute)

    @dataclass
    class CurrentDate(Property):
        """現在年月日設定(0x98)"""

        value: date = date(2000, 1, 1)
        """日時"""

        def __post_init__(self):
            self.code = 0x98
            self.access_rules = [Access.GET, Access.SET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.CurrentDate":
            if len(data) != 4:
                raise ValueError(
                    f"Invalid data length: expected 4 bytes, got {len(data)}"
                )

            value = date(int.from_bytes(data[0:2], byteorder="big"), data[2], data[3])
            return cls(value)

        def encode(self) -> bytes:
            return struct.pack(
                ">HBB", self.value.year, self.value.month, self.value.day
            )

    @dataclass
    class PowerLimitSetting(Property):
        """電力制限設定(0x99)"""

        value: Optional[int] = None
        """制限値(W)"""

        def __post_init__(self):
            self.code = 0x99
            self.access_rules = [Access.GET, Access.SET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.PowerLimitSetting":
            if len(data) != 2:
                raise ValueError(
                    f"Invalid data length: expected 2 bytes, got {len(data)}"
                )

            value = int.from_bytes(data, byteorder="big")
            return cls(value)

        def encode(self) -> bytes:
            if self.value is None:
                raise ValueError("Value must be set before encoding.")
            return struct.pack(">H", self.value)

    @dataclass
    class CumulativeOperatingTime(Property):
        """積算運転時間(0x9A)"""

        class Unit(IntEnum):
            SECOND = 0x41
            MINUTE = 0x42
            HOUR = 0x43
            DAY = 0x44

        unit: Unit = Unit.HOUR
        """単位"""

        value: int = 0
        """積算運転時間"""

        def __post_init__(self):
            self.code = 0x9A
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.CumulativeOperatingTime":
            if len(data) != 5:
                raise ValueError(
                    f"Invalid data length: expected 5 bytes, got {len(data)}"
                )

            unit = cls.Unit(data[0])
            value = int.from_bytes(data[1:5], byteorder="big")
            return cls(unit, value)

        def encode(self) -> bytes:
            return struct.pack(">BI", self.unit.value, self.value)

    @dataclass
    class PropertyMap(Property):
        epc_list: Optional[list[int]] = field(default_factory=list)
        """EPC一覧"""

        @property
        def count(self) -> int:
            """プロパティ数"""
            return len(self.epc_list)

        @classmethod
        def decode(cls, data: bytes) -> "BaseProperty.PropertyMap":
            if len(data) < 1:
                raise ValueError(
                    f"Invalid data length: expected at least 1 byte, got {len(data)}"
                )

            count = data[0]

            if count < 16:
                if len(data) != 1 + count:
                    raise ValueError(
                        f"Invalid data length: expected {1 + count} bytes, got {len(data)}"
                    )
                epc_list = list(data[1:])
            else:
                if len(data) != 17:
                    raise ValueError(
                        f"Invalid data length: expected 17 bytes, got {len(data)}"
                    )
                epc_list = []
                for byte_index in range(16):
                    byte_value = data[byte_index + 1]
                    for bit_index in range(8):
                        if (byte_value >> (7 - bit_index)) & 1:
                            epc = 0xF0 + byte_index - (bit_index * 0x10)
                            epc_list.append(epc)

            return cls(sorted(epc_list))

        def encode(self) -> bytes:
            if self.count < 16:
                return bytes([self.count] + self.epc_list)
            else:
                bitmap = [0x00] * 16
                for epc in self.epc_list:
                    if not 0x80 <= epc <= 0xFF:
                        continue

                    byte_index = epc % 0x10
                    bit_index = (epc >> 4) - 8
                    bitmap[byte_index] |= 1 << bit_index
                return bytes([self.count] + bitmap)

    @dataclass
    class SetMPropertyMap(PropertyMap):
        """SetMプロパティマップ(0x9B)"""

        def __post_init__(self):
            self.code = 0x9B
            self.access_rules = [Access.GET]

    @dataclass
    class GetMPropertyMap(PropertyMap):
        """GetMプロパティマップ(0x9C)"""

        def __post_init__(self):
            self.code = 0x9C
            self.access_rules = [Access.GET]

    @dataclass
    class ChangeAnnoPropertyMap(PropertyMap):
        """状変アナウンスプロパティマップ(0x9D)"""

        def __post_init__(self):
            self.code = 0x9D
            self.access_rules = [Access.GET]

    @dataclass
    class SetPropertyMap(PropertyMap):
        """Setプロパティマップ(0x9E)"""

        def __post_init__(self):
            self.code = 0x9E
            self.access_rules = [Access.GET]

    @dataclass
    class GetPropertyMap(PropertyMap):
        """Getプロパティマップ(0x9F)"""

        def __post_init__(self):
            self.code = 0x9F
            self.access_rules = [Access.GET]
