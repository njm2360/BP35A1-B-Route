from dataclasses import dataclass, field

from app.echonet.property.base_property import Property
from app.echonet.object.access import Access
from app.echonet.protocol.eoj import EnetObject, EnetObjectHeader


class NodeProfile:
    @dataclass
    class InstanceListNotify(Property):
        """インスタンスリスト通知"""

        count: int = 0
        """通報インスタンス数"""
        enet_objs: list[EnetObject] = field(default_factory=list)
        """ECHONETオブジェクトコード"""

        def __post_init__(self):
            self.code = 0xD5
            self.access_rules = [Access.ANNO]

        @classmethod
        def decode(cls, data: bytes) -> "NodeProfile.InstanceListNotify":
            if len(data) < 1:
                raise ValueError("Invalid data: at least 1 byte is required for count.")

            count = data[0]

            expected_length = 1 + count * 3
            if len(data) != expected_length:
                raise ValueError(
                    f"Invalid data length: expected {expected_length} bytes, got {len(data)}"
                )

            enet_objs = []
            index = 1

            for _ in range(count):
                enet_objs.append(EnetObject.decode(data[index : index + 3]))
                index += 3

            return cls(count, enet_objs)

        def encode(self) -> bytes:
            data = bytearray([self.count])
            for obj in self.enet_objs:
                data.extend(obj.encode())

            return bytes(data)
