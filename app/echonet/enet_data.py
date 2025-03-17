from dataclasses import dataclass
from typing import Optional

from app.echonet.protocol.eoj import EnetObject
from app.echonet.protocol.esv import EnetService


@dataclass(frozen=True)
class EchonetData:
    """ECHONET 送信データ"""

    src_enet_object: EnetObject
    """送信元ECHONETオブジェクト"""

    dst_enet_object: EnetObject
    """送信先ECHONETオブジェクト"""

    enet_service: EnetService
    """ECHONETサービス"""

    properties: tuple[property]
    """ECHONETプロパティ"""

    transaction_id: Optional[int] = None
    """トランザクションID"""
