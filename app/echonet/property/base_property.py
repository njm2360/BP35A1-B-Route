from dataclasses import dataclass
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

        result.append(self.code)  # EPC

        if mode == Access.GET:
            result.append(0x00)  # PDC
            return result
        else:
            result.append(0x01)

        if self._status:
            result.append(0x30)  # EDT
        else:
            result.append(0x31)

        return result


@dataclass
class Location(Property):
    """設置場所(0x81)"""

    status: bool = False
    """状態"""

    def __post_init__(self):
        self._code = 0x80
        self._accessRules = [Access.GET, Access.SET]

    @classmethod
    def decode(self, data: bytes):
        self._status = data == 0x30

    def encode(self, mode: Access) -> list[int]:
        result: list[int] = []

        result.append(self._code)  # EPC

        if mode == Access.GET:
            result.append(0x00)  # PDC
            return result
        else:
            result.append(0x01)

        if self._status:
            result.append(0x30)  # EDT
        else:
            result.append(0x31)

        return result
