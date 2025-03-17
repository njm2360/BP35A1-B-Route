import os
from app.bp35a1.bp35a1 import BP35A1
from app.bp35a1.event import Epan, RxData
from app.echonet.echonet import ECHONET_LITE_PORT
from app.interface.echonet_if import EchonetInterface


EPAN_DATA_JSON = "epan.json"


class BP35A1Interface(EchonetInterface):
    @property
    def packet_size_limit(self) -> int:
        return 1232

    def __init__(self, port: str, id: str, password: str):
        self._bp35a1: BP35A1 = BP35A1(port)
        self._id: str = id
        self._password: str = password
        self._connected_ip: str = None

    async def init(self):
        await self._bp35a1.init(self._id, self._password)

        epan = self._load_epan() or await self._scan_and_save_epan()

        self._connected_ip = await self._bp35a1.connect(epan)

    def _load_epan(self) -> Epan:
        if os.path.exists(EPAN_DATA_JSON):
            try:
                return Epan.from_json(file_path=EPAN_DATA_JSON)
            except Exception as e:
                print(f"EPAN json read failed: {e}")
        return None

    async def _scan_and_save_epan(self) -> Epan:
        epan = await self._bp35a1.scan(init_duration=6)
        if epan is None:
            raise Exception("Epan not found")
        epan.to_json(EPAN_DATA_JSON)
        return epan

    async def send_data(self, data: bytes):
        if not self._connected_ip:
            raise Exception("Not connected")

        await self._bp35a1.send_udp(
            ip_address=self._connected_ip,
            port=ECHONET_LITE_PORT,
            data=data,
        )

    async def get_data(self) -> bytes:
        while True:
            result = await self._bp35a1.get_next_result()

            if isinstance(result, RxData) and result.dst_port == ECHONET_LITE_PORT:
                return result.data
