import struct
from collections import deque

from app.echonet.protocol.ehd import EchonetHeader
from app.echonet.protocol.eoj import EnetObjectHeader
from app.echonet.protocol.esv import EnetService
from app.echonet.object.access import Access
from app.echonet.property.property import Property
from app.echonet.protocol.tid import TransactionId


class ProtocolTx:
    ESV_ACCESS_RULES = {
        EnetService.SetI: [Access.SET],
        EnetService.SetC: [Access.SET],
        EnetService.Get: [Access.GET],
        EnetService.Inf_Req: [Access.ANNO],
        EnetService.SetGet: [Access.SET, Access.GET],
        EnetService.SetRes: [Access.SET],
        EnetService.GetRes: [Access.GET],
        EnetService.Inf: [Access.ANNO],
        EnetService.InfC: [Access.ANNO],
        EnetService.InfcRes: [Access.ANNO],
        EnetService.SetGetRes: [Access.SET, Access.GET],
        EnetService.SetI_Sna: [Access.SET],
        EnetService.SetC_Sna: [Access.SET],
        EnetService.Get_Sna: [Access.GET],
        EnetService.Inf_Sna: [Access.ANNO],
        EnetService.SetGet_Sna: [Access.SET, Access.GET],
    }

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
        self._limitAccessRules = self.ESV_ACCESS_RULES.get(self._enet_service, [])
        self._encode_mode = (
            Access.GET if Access.GET in self._limitAccessRules else Access.SET
        )
        self._packet_size_limit = packet_size_limit

    def add_property(self, property: Property):
        # ToDo 通信仕様の理解がもっと必要、単純ではない

        # if any(rule in self._limitAccessRules for rule in property.accessRules):
        #     self._properties.append(property)
        # else:
        #     raise Exception("Access rule violation")

        self._properties.append(property)

    def make(self, transaction_id: TransactionId) -> list[tuple[int, bytes]]:
        packets = []

        encoded_properties = []
        for prop in self._properties:
            encoded_value = prop.encode(mode=self._encode_mode)
            encoded_properties.append(
                struct.pack("BB", prop.code, len(encoded_value)) + bytes(encoded_value)
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
