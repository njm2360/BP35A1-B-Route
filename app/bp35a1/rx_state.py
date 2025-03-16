from enum import IntEnum, auto


class RxState(IntEnum):
    """受信状態"""

    NORMAL = auto()
    """通常受信"""
    EADDR = auto()
    """WADDR 返信待機 (4-3)"""
    ENEIGHBOR = auto()
    """ENEIGHBOR 返信待機 (4-4)"""
    EPANDESC = auto()
    """EPANDESC 返信待機 (4-5)"""
    EEDSCAN = auto()
    """EEDSCAN 返信待機 (4-6)"""
    EPORT = auto()
    """EPORT 返信待機 (4-7)"""
    SKLL64 = auto()
    """SKLL64 返信待機 (3-29)"""
    PRODUCT_CONFIG_READ = auto()
    """プロダクト設定コマンド 返信待機 (3-31, 3-33)"""
