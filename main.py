import os
import asyncio
from dotenv import load_dotenv

from app.bp35a1.bp35a1 import BP35A1
from app.echonet.classcode import ClassCode, ClassGroupCode

from app.echonet.echonet import ECHONET_LITE_PORT, ProtocolTx, ProtocolRx
from app.echonet.protocol.eoj import EOJ
from app.echonet.protocol.esv import ESV
from app.echonet.property.home_equipment_device.low_voltage_smart_pm import (
    MomentCurrent,
    MomentPower,
)
from app.echonet.property.profile.node_profile import InstanceListNotify


async def run():
    load_dotenv()

    RB_ID = os.getenv("RB_ID")
    RB_PASSWORD = os.getenv("RB_PASSWORD")

    EPAN_DATA_JSON = "epan.json"

    CTRL_ENET_OBJ = EOJ.EnetObj(
        classGroupCode=ClassGroupCode.ManagerOpDevice,
        classCode=ClassCode.Controller,
        instanceCode=0x01,
    )

    sm_enet_obj: EOJ.EnetObj = None
    bp35a1 = BP35A1(port="COM3")
    rx_task = asyncio.create_task(bp35a1.proc_rx())

    try:
        await bp35a1.init(RB_ID, RB_PASSWORD)

        if os.path.exists(EPAN_DATA_JSON):
            epan = BP35A1.Epan.from_json(file_path=EPAN_DATA_JSON)
        else:
            epan = await bp35a1.scan(init_duration=6)
            if epan is None:
                raise Exception("Epan not found")

            epan.to_json(EPAN_DATA_JSON)

        pan_ip_address = await bp35a1.connect(epan)

        while sm_enet_obj is None:
            result = await bp35a1.get_next_result()

            if isinstance(result, BP35A1.RxData):
                properties = ProtocolRx().proc(data=result.data)
                for property in properties:
                    if isinstance(property, InstanceListNotify):
                        sm_enet_obj = property.enet_objs[0]

        protocolTx = ProtocolTx(
            eoj=EOJ(src=CTRL_ENET_OBJ, dst=sm_enet_obj),
            esv=ESV.Get,
        )

        protocolTx.add(MomentPower())
        # protocolTx.add(MomentCurrent())
        data = protocolTx.make()

        await bp35a1.send_udp(pan_ip_address, ECHONET_LITE_PORT, data)

        while True:
            result = await bp35a1.get_next_result()

            if isinstance(result, BP35A1.RxData):
                properties = ProtocolRx().proc(data=result.data)
                for property in properties:
                    print(property)

                await bp35a1.send_udp(pan_ip_address, 3610, data)
            elif isinstance(result, BP35A1.Event):
                if result.code != BP35A1.EventCode.UDP_SEND_OK:
                    print(result)

    except asyncio.CancelledError:
        pass

    finally:
        rx_task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
