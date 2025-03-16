from enum import IntEnum
from typing import Optional
from dataclasses import dataclass

from app.repository.json_repo import JsonSerializable


class EventData:
    pass


class EventCode(IntEnum):
    """イベントコード"""

    RECV_NS = 0x01
    """NS を受信した"""
    RECV_NA = 0x02
    """NA を受信した"""
    RECV_ECHO_REQ = 0x05
    """Echo Request を受信した"""
    ED_SCAN_OK = 0x1F
    """ED スキャンが完了した"""
    RECV_BEACON = 0x20
    """Beacon を受信した"""
    UDP_SEND_OK = 0x21
    """UDP 送信処理が完了した"""
    ACTIVE_SCAN_OK = 0x22
    """アクティブスキャンが完了した"""
    PANA_CONNECT_ERROR = 0x24
    """PANA による接続過程でエラーが発生した（接続が完了しなかった）"""
    PANA_CONNECT_OK = 0x25
    """PANA による接続が完了した"""
    RECV_SESSION_END = 0x26
    """接続相手からセッション終了要求を受信した"""
    PANA_SESSION_END_OK = 0x27
    """PANA セッションの終了に成功した"""
    PANA_SESSION_END_TIMEOUT = 0x28
    """PANA セッションの終了要求に対する応答がなくタイムアウトした（セッションは終了）"""
    SESITON_LIFETIME_EXPIRE = 0x29
    """セッションのライフタイムが経過して期限切れになった"""
    SEND_LIMIT_EXCEED = 0x32
    """ARIB108 の送信総和時間の制限が発動した"""
    SEND_LIMIT_CANCELED = 0x33
    """送信総和時間の制限が解除された"""


@dataclass
class Event(EventData):
    """イベント"""

    code: EventCode
    """イベントコード"""
    sender: str
    """送信元アドレス"""


@dataclass
class Epan(EventData, JsonSerializable):
    """EPAN"""

    channel: Optional[int] = None
    """論理チャネル番号"""
    channel_page: Optional[int] = None
    """チャネルページ"""
    pan_id: Optional[int] = None
    """PAN ID"""
    mac_address: Optional[str] = None
    """応答元MACアドレス"""
    lqi: Optional[int] = None
    """受信RSSI"""
    pair_id: Optional[str] = None
    """ペアリングID"""

    def is_complete(self) -> bool:
        return all(
            v is not None
            for v in [
                self.channel,
                self.channel_page,
                self.pan_id,
                self.mac_address,
                self.lqi,
                self.pair_id,
            ]
        )


@dataclass
class RxData(EventData):
    """受信データ"""

    src_addr: str
    """送信元IPアドレス"""
    dst_addr: str
    """送信先IPアドレス"""
    src_port: int
    """送信元ポート"""
    dst_port: int
    """送信先ポート"""
    src_mac: str
    """送信元MACアドレス"""
    secured: bool
    """暗号化"""
    length: int
    """受信データ長"""
    data: bytes
    """受信データ"""
