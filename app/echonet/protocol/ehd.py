from enum import IntEnum
from dataclasses import dataclass


@dataclass
class EchonetHeader:
    """ECHONET Lite ヘッダ（EHD）"""

    class Header1(IntEnum):
        ECHONET_LITE = 0x10
        """ECHONET Lite規格"""

    class Header2(IntEnum):
        FORMAT1 = 0x81
        """形式１"""
        FORMAT2 = 0x82
        """形式２"""

    ehd1: Header1
    """ECHONET Lite ヘッダ１（EHD１）"""
    ehd2: Header2
    """ECHONET Lite ヘッダ２（EHD２）"""

    def encode(self) -> list[int]:
        return [int(self.ehd1), int(self.ehd2)]
