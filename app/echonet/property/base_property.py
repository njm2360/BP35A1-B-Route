from dataclasses import dataclass
from typing import Optional, Union

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
        result: list[int] = []

        result.append(self.code)

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
        result: list[int] = []

        result.append(self.code)

        if mode == Access.GET:
            result.append(0x00)
        else:
            raise NotImplementedError()

        return result
