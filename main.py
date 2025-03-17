import os
import asyncio
import traceback
from dotenv import load_dotenv

from app.echonet.echonet import Echonet
from app.echonet.protocol.eoj import EnetObject
from app.echonet.protocol.esv import EnetService
from app.echonet.enet_data import EchonetData
from app.echonet.property.home_equipment_device.low_voltage_smart_pm import (
    LowVoltageSmartPm,
)
from app.echonet.property.profile.node_profile import NodeProfile
from app.echonet.object.classcode import ClassCode, ClassGroupCode
from app.interface.bp35a1_if import BP35A1Interface


async def main_task(echonet: Echonet):

    CTRL_ENET_OBJ = EnetObject(
        classGroupCode=ClassGroupCode.ManagerOpDevice,
        classCode=ClassCode.Controller,
        instanceCode=0x01,
    )

    sm_enet_obj: EnetObject = None

    # インスタンスリスト取得
    while sm_enet_obj is None:
        received_data = await echonet.get_received_data()

        for prop in received_data.properties:
            if isinstance(prop, NodeProfile.InstanceListNotify):
                sm_enet_obj = prop.enet_objs[0]

    # 瞬時電力計測値 要求
    request_data = EchonetData(
        src_enet_object=CTRL_ENET_OBJ,
        dst_enet_object=sm_enet_obj,
        enet_service=EnetService.Get,
        properties=[LowVoltageSmartPm.MomentPower()],
    )

    await echonet.send_data(request_data)

    while True:
        received_data = await echonet.get_received_data()

        for prop in received_data.properties:
            print(prop)

            if isinstance(prop, LowVoltageSmartPm.MomentPower):
                # 取得後に瞬時電力計測値を継続要求
                await echonet.send_data(request_data)


async def run():
    load_dotenv()

    SERIAL_PORT = os.getenv("SERIAL_PORT")
    RB_ID = os.getenv("RB_ID")
    RB_PASSWORD = os.getenv("RB_PASSWORD")

    bp35a1_interface = BP35A1Interface(SERIAL_PORT, RB_ID, RB_PASSWORD)
    await bp35a1_interface.init()

    device_objects = []
    echonet = Echonet(device_objects, bp35a1_interface)

    tasks = [
        asyncio.create_task(echonet.proc_tx_task()),
        asyncio.create_task(echonet.proc_rx_task()),
        asyncio.create_task(main_task(echonet)),
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
