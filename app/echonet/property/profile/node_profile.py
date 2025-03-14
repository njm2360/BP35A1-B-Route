from dataclasses import dataclass, field

from app.echonet.property.base_property import Property
from app.echonet.protocol.access import Access
from app.echonet.protocol.eoj import EOJ


@dataclass
class InstanceListNotify(Property):
    """インスタンスリスト通知"""

    count: int
    enet_objs: list[EOJ.EnetObj]

    code: int = field(init=False, default=0xD5)
    accessRules: list[Access] = field(init=False, default_factory=lambda: [Access.ANNO])

    @classmethod
    def decode(cls, data: bytes) -> "InstanceListNotify":
        count = data[0]
        enet_objs = []
        index = 1

        for i in range(count):
            enet_objs.append(EOJ.decode_single(data[index : index + 3]))
            index += 3

        return cls(count, enet_objs)

    def encode(self, mode: Access) -> list[int]:
        raise NotImplementedError()
