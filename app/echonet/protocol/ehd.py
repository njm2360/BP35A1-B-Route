from dataclasses import dataclass
from enum import IntEnum


@dataclass
class EHD:
    """ECHONET Lite ヘッダ（EHD）"""

    class EHD1(IntEnum):
        ECHONET_LITE = 0x10
        """ECHONET Lite規格"""

    class EHD2(IntEnum):
        FORMAT1 = 0x81
        """形式１"""
        FORMAT2 = 0x82
        """形式２"""

    ehd1: EHD1
    """ECHONET Lite ヘッダ１（EHD１）"""
    ehd2: EHD2
    """ECHONET Lite ヘッダ２（EHD２）"""

    def encode(self) -> list[int]:
        return [int(self.ehd1), int(self.ehd2)]
