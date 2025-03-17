import struct
from typing import Optional

from app.echonet.enet_data import EchonetData

from app.echonet.protocol.ehd import EchonetHeader
from app.echonet.protocol.eoj import EnetObjectHeader
from app.echonet.protocol.esv import EnetService

from app.echonet.property.property import Property
from app.echonet.protocol.decoder import getPropertyDecoder


class ProtocolRx:
    @classmethod
    def proc(cls, data: bytes) -> Optional[EchonetData]:
        if not cls._is_valid_protocol(data):  # EHD
            return None

        if len(data) < 12:
            raise ValueError(
                f"Invalid data length: expected at least 12 bytes, got {len(data)}"
            )

        transaction_id = struct.unpack(">H", data[2:4])[0]  # TID
        enet_object_header = EnetObjectHeader.decode(data[4:10])  # EOJ
        enet_service = EnetService(data[10])  # ESV
        operation_count = data[11]  # OPC

        # print(
        #     f"TID: {transaction_id}, ESV: 0x{enet_service:02x}, OPC: {operation_count}"
        # )

        properties: list[Property] = []

        if operation_count > 0:
            index = 12

            for _ in range(operation_count):
                if len(data) < index + 2:
                    raise ValueError(
                        f"Unexpected end of data at index {index}: insufficient EPC and PDC bytes"
                    )

                epc, pdc = struct.unpack("BB", data[index : index + 2])
                index += 2

                if pdc == 0:
                    continue

                if len(data) < index + pdc:
                    raise ValueError(
                        f"Unexpected end of data at index {index}: expected {pdc} bytes for EDT, but got {len(data) - index}"
                    )

                edt = data[index : index + pdc]
                index += pdc

                decoder = getPropertyDecoder(
                    enet_object=enet_object_header.src, epc=epc
                )
                if decoder:
                    property = decoder(edt)
                    properties.append(property)

            if index < len(data):
                raise ValueError("Excess data found after processing all properties")

        result = EchonetData(
            src_enet_object=enet_object_header.src,
            dst_enet_object=enet_object_header.dst,
            enet_service=enet_service,
            transaction_id=transaction_id,
            properties=tuple(properties),
        )

        return result

    @classmethod
    def _is_valid_protocol(cls, data: bytes) -> bool:
        return len(data) >= 2 and data[:2] == bytes(
            [EchonetHeader.Header1.ECHONET_LITE, EchonetHeader.Header2.FORMAT1]
        )
