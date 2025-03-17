import asyncio
from typing import Final
from asyncio import Queue
from dataclasses import dataclass, field

from app.echonet.object.enet_object import EnetObject
from app.echonet.property.property import Property
from app.echonet.protocol.eoj import EnetObjectHeader
from app.echonet.protocol.esv import EnetService
from app.echonet.protocol.protocol_rx import ProtocolRx
from app.echonet.protocol.protocol_tx import ProtocolTx
from app.echonet.protocol.tid import TransactionId
from app.echonet.enet_data import EchonetData
from app.interface.echonet_if import EchonetInterface

ECHONET_LITE_PORT: Final[int] = 3610


@dataclass
class DeviceObject:
    """機器オブジェクト"""

    enet_object: EnetObject
    """ECHONETオブジェクト"""

    properties: list[Property] = field(default_factory=list)
    """プロパティ一覧"""


class Echonet:
    def __init__(self, device_objects: list[DeviceObject], interface: EchonetInterface):
        self._device_objects: list[DeviceObject] = device_objects
        self._interface: EchonetInterface = interface

        self._transfer_data: Queue[EchonetData] = Queue()
        """送信データ"""
        self._receive_data: Queue[EchonetData] = Queue()
        """受信データ"""

        self._transaction_id: TransactionId = TransactionId()
        """トランザクションID"""
        self._pending_transactions: dict[int, asyncio.Event] = {}
        """未完了トランザクション"""

    async def proc_tx_task(self):
        while True:
            data = await self._transfer_data.get()

            protocol_tx = ProtocolTx(
                enet_object_header=EnetObjectHeader(
                    src=data.src_enet_object, dst=data.dst_enet_object
                ),
                enet_service=data.enet_service,
                packet_size_limit=self._interface.packet_size_limit,
            )

            wait_response = data.enet_service in {EnetService.Get, EnetService.SetC}

            for property in data.properties:
                protocol_tx.add_property(property)

            send_datas = protocol_tx.make(self._transaction_id)

            for tid, send_data in send_datas:
                if wait_response:
                    event = asyncio.Event()
                    self._pending_transactions[tid] = event

                await self._interface.send_data(send_data)

                if wait_response:
                    try:
                        await asyncio.wait_for(event.wait(), timeout=30)
                    except asyncio.TimeoutError:
                        print(f"TID {tid}: Response Timeout")
                    finally:
                        self._pending_transactions.pop(tid, None)

    async def proc_rx_task(self):
        while True:
            data = await self._interface.get_data()
            enet_data = ProtocolRx.proc(data)

            if not enet_data:
                continue

            await self._receive_data.put(enet_data)

            # 送信したTIDに対応するレスポンスなら送信待機を解除
            if enet_data.transaction_id in self._pending_transactions:
                self._pending_transactions[enet_data.transaction_id].set()

            # 他にもやることはたくさんあるがとりあえずInfCの返信だけ実装
            if enet_data.enet_service == EnetService.InfC:
                # srcとdstを入れ替え,対応するESVをセットして同一TIDで返信
                response = EchonetData(
                    src_enet_object=enet_data.dst_enet_object,
                    dst_enet_object=enet_data.src_enet_object,
                    enet_service=EnetService.InfcRes,
                    transaction_id=enet_data.transaction_id,
                    properties=enet_data.properties,
                )
                await self._transfer_data.put(response)

    async def send_data(self, data: EchonetData):
        await self._transfer_data.put(data)

    async def get_received_data(self) -> EchonetData:
        return await self._receive_data.get()
