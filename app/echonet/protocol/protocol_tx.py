import struct
from collections import deque

from app.echonet.protocol.ehd import EchonetHeader
from app.echonet.protocol.eoj import EnetObjectHeader
from app.echonet.protocol.esv import EnetService
from app.echonet.object.access import Access
from app.echonet.property.property import Property
from app.echonet.protocol.tid import TransactionId


class ProtocolTx:
    def __init__(
        self,
        enet_object_header: EnetObjectHeader,
        enet_service: EnetService,
        enet_header=EchonetHeader(
            ehd1=EchonetHeader.Header1.ECHONET_LITE, ehd2=EchonetHeader.Header2.FORMAT1
        ),
        packet_size_limit: int = None,
    ):
        self._enet_header = enet_header
        self._enet_object_header = enet_object_header
        self._enet_service = enet_service
        self._properties: deque[Property] = deque()
        self._packet_size_limit = packet_size_limit

    def add_property(self, property: Property):
        # ToDo 通信仕様の理解がもっと必要、単純ではない

        self._properties.append(property)

    def make(self, transaction_id: TransactionId) -> list[tuple[int, bytes]]:
        packets = []

        encoded_properties = []
        for prop in self._properties:
            encoded_value = (
                b""
                if self._enet_service in {EnetService.Get, EnetService.Inf_Req}
                else prop.encode()
            )
            encoded_properties.append(
                struct.pack("BB", prop.code, len(encoded_value)) + encoded_value
            )

        current_properties = []
        current_length = 12

        for prop in encoded_properties:
            prop_length = len(prop)

            if (
                self._packet_size_limit
                and current_length + prop_length > self._packet_size_limit
            ):
                current_tid = transaction_id.value
                packets.append(
                    (current_tid, self._create_packet(current_tid, current_properties))
                )
                transaction_id.increment()
                current_properties = [prop]
                current_length = 12 + prop_length
            else:
                current_properties.append(prop)
                current_length += prop_length

        if current_properties:
            current_tid = transaction_id.value
            packets.append(
                (current_tid, self._create_packet(current_tid, current_properties))
            )
            transaction_id.increment()

        return packets

    def _create_packet(self, tid: int, properties: list[bytes]) -> bytes:
        packet = bytearray()

        packet.extend(self._enet_header.encode())  # EHD
        packet.extend(struct.pack(">H", tid))  # TID
        packet.extend(self._enet_object_header.encode())  # EOJ
        packet.append(int(self._enet_service))  # ESV
        packet.append(len(properties))  # OPC
        packet.extend(b"".join(properties))  # EPC + PDC + EDT

        return bytes(packet)
