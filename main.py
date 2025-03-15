import os
import asyncio
import traceback
from dotenv import load_dotenv

from app.bp35a1.bp35a1 import BP35A1
from app.echonet.classcode import ClassCode, ClassGroupCode

from app.echonet.echonet import ECHONET_LITE_PORT, ProtocolTx, ProtocolRx
from app.echonet.property.home_equipment_device.low_voltage_smart_pm import (
    LowVoltageSmartPm,
)
from app.echonet.property.profile.node_profile import NodeProfile
from app.echonet.protocol.eoj import EnetObject, EnetObjectHeader
from app.echonet.protocol.esv import EnetService


async def main_task(bp35a1: BP35A1):
    RB_ID = os.getenv("RB_ID")
    RB_PASSWORD = os.getenv("RB_PASSWORD")

    EPAN_DATA_JSON = "epan.json"

    CTRL_ENET_OBJ = EnetObject(
        classGroupCode=ClassGroupCode.ManagerOpDevice,
        classCode=ClassCode.Controller,
        instanceCode=0x01,
    )

    sm_enet_obj: EnetObject = None

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
            receive_data = ProtocolRx.proc(data=result.data)
            for property in receive_data.properties:
                if isinstance(property, NodeProfile.InstanceListNotify):
                    sm_enet_obj = property.enet_objs[0]

    protocolTx = ProtocolTx(
        enet_object_header=EnetObjectHeader(src=CTRL_ENET_OBJ, dst=sm_enet_obj),
        enet_service=EnetService.Get,
    )
    protocolTx.add(LowVoltageSmartPm.MomentPower())
    data = protocolTx.make()
    await bp35a1.send_udp(pan_ip_address, ECHONET_LITE_PORT, data)

    while True:
        result = await bp35a1.get_next_result()

        if isinstance(result, BP35A1.RxData):
            receive_data = ProtocolRx.proc(data=result.data)
            for property in receive_data.properties:
                print(property)
                if isinstance(property, LowVoltageSmartPm.MomentPower):
                    protocolTx.add(LowVoltageSmartPm.MomentPower())
                    data = protocolTx.make()
                    await bp35a1.send_udp(pan_ip_address, ECHONET_LITE_PORT, data)

        elif isinstance(result, BP35A1.Event):
            if result.code != BP35A1.EventCode.UDP_SEND_OK:
                print(result)


async def run():
    load_dotenv()

    SERIAL_PORT = os.getenv("SERIAL_PORT")

    bp35a1 = BP35A1(port=SERIAL_PORT)

    tasks = [
        asyncio.create_task(bp35a1.proc_rx()),
        asyncio.create_task(main_task(bp35a1)),
    ]

    try:
        done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

        for task in done:
            try:
                result = task.result()
                print(f"Task completed successfully: {result}")
            except asyncio.CancelledError:
                print("Task was cancelled.")
            except Exception as e:
                print(f"Task failed with exception: {e}")
                traceback.print_exc()

    except KeyboardInterrupt:
        all_tasks = asyncio.all_tasks()

        for task in all_tasks:
            task.cancel()

        await asyncio.gather(*all_tasks, return_exceptions=True)

    finally:
        await asyncio.sleep(0)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
