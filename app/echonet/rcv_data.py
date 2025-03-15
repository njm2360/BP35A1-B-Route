from datetime import datetime
from dataclasses import dataclass

from app.echonet.protocol.eoj import EnetObject
from app.echonet.protocol.esv import EnetService


@dataclass(frozen=True)
class EchonetReceiveData:
    """ECHONET 受信データ"""

    received_at: datetime
    """受信日時"""

    src_enet_object: EnetObject
    """送信元ECHONETオブジェクト"""

    dst_enet_object: EnetObject
    """送信先ECHONETオブジェクト"""

    enet_service: EnetService
    """ECHONETサービス"""

    transaction_id: int
    """トランザクションID"""

    properties: tuple[property]
    """ECHONETプロパティ"""
