from enum import IntEnum


class LocationCode(IntEnum):
    LIVING_ROOM = 0b0001
    """居間、リビング"""
    DINING_ROOM = 0b0010
    """食堂、ダイニング"""
    KITCHEN = 0b0011
    """台所、キッチン"""
    BATHROOM = 0b0100
    """浴室、バス"""
    TOILET = 0b0101
    """トイレ"""
    WASHROOM = 0b0110
    """洗面所、脱衣所"""
    HALLWAY = 0b0111
    """廊下"""
    ROOM = 0b1000
    """部屋"""
    STAIRS = 0b1001
    """階段"""
    ENTRANCE = 0b1010
    """玄関"""
    STORAGE = 0b1011
    """納戸"""
    GARDEN = 0b1100
    """庭、外周"""
    GARAGE = 0b1101
    """車庫"""
    BALCONY = 0b1110
    """ベランダ、バルコニー"""
    OTHER = 0b1111
    """その他"""


class SpecialLocationCode(IntEnum):
    NOT_SET = 0x00
    """設置場所未設定"""
    POSITION_INFORMATION = 0x01
    """位置情報定義"""
    UNDEFINED = 0xFF
    """設置場所不定"""
