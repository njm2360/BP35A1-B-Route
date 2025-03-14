import re
import asyncio
import aioserial
from asyncio import Queue
from enum import IntEnum, StrEnum
from typing import Optional, Union
from dataclasses import dataclass

from app.bp35a1.exception import CommandError, PANAConnectError, TxProhibisionError
from app.repository.json_repo import JsonSerializable


class BP35A1:
    class EventData:
        pass

    class EventCode(IntEnum):
        RECV_NS = 0x01
        RECV_NA = 0x02
        RECV_ECHO_REQ = 0x05
        ED_SCAN_OK = 0x1F
        RECV_BEACON = 0x20
        UDP_SEND_OK = 0x21
        ACTIVE_SCAN_OK = 0x22
        PANA_CONNECT_ERROR = 0x24
        PANA_CONNECT_OK = 0x25
        RECV_SESSION_END = 0x26
        PANA_SESSION_END_OK = 0x27
        PANA_SESSION_END_TIMEOUT = 0x28
        SESITON_LIFETIME_EXPIRE = 0x29
        SEND_LIMIT_EXCEED = 0x32
        SEND_LIMIT_CANCELED = 0x33

    @dataclass
    class Event(EventData):
        code: "BP35A1.EventCode"
        sender: str

    @dataclass
    class Epan(EventData, JsonSerializable):
        channel: Optional[int] = None
        channel_page: Optional[int] = None
        pan_id: Optional[int] = None
        mac_address: Optional[str] = None
        lqi: Optional[int] = None
        pair_id: Optional[str] = None

        def is_complete(self) -> bool:
            return all(
                v is not None
                for v in [
                    self.channel,
                    self.channel_page,
                    self.pan_id,
                    self.mac_address,
                    self.lqi,
                    self.pair_id,
                ]
            )

    @dataclass
    class RxData(EventData):
        src_addr: str
        dst_addr: str
        src_port: int
        dst_port: int
        src_mac: str
        secured: bool
        length: int
        data: bytes

    class RxState(IntEnum):
        NORMAL = 0
        EADDR = 1
        ENEIGHBOR = 2
        EPANDESC = 3
        EEDSCAN = 4
        EPORT = 5
        SKLL64 = 10
        PRODUCT_CONFIG_READ = 40

    class NewLineCode(StrEnum):
        CRLF = "\r\n"
        CR = "\r"

    def __init__(self, port: str):
        self._ser = aioserial.AioSerial(port=port, baudrate=115200, timeout=3)
        self._newline_code = self.NewLineCode.CRLF
        self._rx_state = self.RxState.NORMAL
        self._udp_tx_allowed = False
        self._event_queue: Queue[Union[BP35A1.EventData]] = Queue()
        self._result_queue: Queue[str] = Queue()
        self._response_queue: Queue[str] = Queue()

    async def init(self, id: str, password: str):
        await self._send_command(f"SKRESET")
        await self._send_command(f"SKSREG SFE 0")
        await self._send_command(f"SKSETRBID {id}")
        await self._send_command(f"SKSETPWD {len(password):X} {password}")

    async def scan(self, init_duration: int = 4) -> Optional[Epan]:
        duration = init_duration
        epan = None

        print("Scanning...")

        while duration <= 7:
            command = f"SKSCAN 2 FFFFFFFF {duration}"
            await self._send_command(command)

            try:
                while True:
                    result = await asyncio.wait_for(self.get_next_result(), timeout=30)
                    if isinstance(result, BP35A1.Epan):
                        epan = result
                    elif isinstance(result, BP35A1.Event):
                        if result.code == BP35A1.EventCode.ACTIVE_SCAN_OK:
                            break
            except asyncio.TimeoutError:
                pass

            if epan:
                return epan

            duration += 1

        return epan

    async def connect(self, epan: Epan) -> str:
        command = f"SKSREG S2 {epan.channel:X}"
        await self._send_command(command)

        command = f"SKSREG S3 {epan.pan_id:X}"
        await self._send_command(command)

        command = f"SKLL64 {epan.mac_address}"
        ip_address = await self._send_command(command)

        print("Connecting...")

        command = f"SKJOIN {ip_address}"
        await self._send_command(command)

        try:
            while True:
                result = await asyncio.wait_for(self.get_next_result(), timeout=30)
                if isinstance(result, BP35A1.Event):
                    if result.code == BP35A1.EventCode.PANA_CONNECT_OK:
                        print(f"PANA connect OK {ip_address}")
                        return ip_address
                    elif result.code == BP35A1.EventCode.PANA_CONNECT_ERROR:
                        raise PANAConnectError()
        except asyncio.TimeoutError:
            pass

    async def send_udp(
        self,
        ip_address: str,
        port: int,
        data: bytes,
        handle: int = 1,
        security: bool = True,
    ):
        if self._udp_tx_allowed is False:
            raise TxProhibisionError()

        command = f"SKSENDTO {handle} {ip_address} {port:04X} {1 if security else 2} {len(data):04X}"
        await self._send_command(command, data)

    async def proc_rx(self):
        buffer: bytes = b""

        while self._ser.is_open:
            data = await self._ser.read_async()

            if not data:
                continue
            buffer += data

            if self._newline_code == self.NewLineCode.CRLF and buffer.endswith(b"\r\n"):
                await self._process_line(buffer)
                buffer = b""
            elif self._newline_code == self.NewLineCode.CR and data == b"\r":
                await self._process_line(buffer)
                buffer = b""

    async def _process_line(self, data: bytes):
        # print(f"=> {data}")
        line = data.decode().strip()

        match self._rx_state:
            case self.RxState.NORMAL:
                if line.startswith("ERXUDP"):  # 4-1
                    datas = line.split(" ")
                    rxdata = self.RxData(
                        src_addr=datas[1],
                        dst_addr=datas[2],
                        src_port=int(datas[3], 16),
                        dst_port=int(datas[4], 16),
                        src_mac=datas[5],
                        secured=datas[6] == "1",
                        length=int(datas[7], 16),
                        data=bytes.fromhex(datas[8]),
                    )
                    await self._event_queue.put(rxdata)
                elif line.startswith("EPONG"):  # 4-2
                    pass
                elif line == "EADDR":  # 4-3
                    pass
                elif line == "ENEIGHBOR":  # 4-4
                    pass
                elif line == "EPANDESC":  # 4-5
                    self._rx_state = self.RxState.EPANDESC
                    self._epan = BP35A1.Epan()
                elif line == "EEDSCAN":  # 4-6
                    pass
                elif line == "EPORT":  # 4-7
                    pass
                elif line.startswith("EVENT"):  # 4-8
                    datas = line.split(" ")
                    event = self.Event(
                        code=BP35A1.EventCode(int(datas[1], 16)), sender=datas[2]
                    )

                    match event.code:
                        case BP35A1.EventCode.PANA_CONNECT_OK:
                            self._udp_tx_allowed = True
                        case BP35A1.EventCode.SESITON_LIFETIME_EXPIRE:
                            self._udp_tx_allowed = False

                    await self._event_queue.put(event)
                elif line.startswith("OK") or line.startswith("FAIL"):
                    await self._result_queue.put(line)
                else:
                    await self._response_queue.put(line)
            case self.RxState.EPANDESC:
                match = re.match(r"\s*(.+?):(.+)", line)
                if match:
                    key, value = match.groups()
                    value = value.strip()

                    if key == "Channel":
                        self._epan.channel = int(value, 16)
                    elif key == "Channel Page":
                        self._epan.channel_page = int(value, 16)
                    elif key == "Pan ID":
                        self._epan.pan_id = int(value, 16)
                    elif key == "Addr":
                        self._epan.mac_address = value
                    elif key == "LQI":
                        self._epan.lqi = int(value, 16)
                    elif key == "PairID":
                        self._epan.pair_id = value

                    if self._epan.is_complete():
                        self._rx_state = self.RxState.NORMAL
                        await self._event_queue.put(self._epan)
            case self.RxState.SKLL64:
                if not line.startswith("FAIL"):
                    await self._response_queue.put(line)
                    await self._result_queue.put("OK")
                else:
                    await self._result_queue.put(line)
                self._rx_state = self.RxState.NORMAL
            case self.RxState.PRODUCT_CONFIG_READ:
                if line.startswith("OK"):
                    datas = line.split(" ", 1)
                    await self._response_queue.put(datas[1])
                    await self._result_queue.put(datas[0])
                else:
                    await self._result_queue.put(line)
                self._rx_state = self.RxState.NORMAL

    async def _send_command(self, command: str, data: bytes = None) -> str:
        self._result_queue = Queue()
        self._response_queue = Queue()

        if command.startswith(("WOPT", "WUART", "ROPT", "RUART")):
            self._newline_code = self.NewLineCode.CR
            if command.startswith(("ROPT", "RUART")):
                self._rx_state = self.RxState.PRODUCT_CONFIG_READ
        else:
            self._newline_code = self.NewLineCode.CRLF

        if command.startswith("SKLL64"):
            self._rx_state = self.RxState.SKLL64

        if data:
            send_data = command.encode() + b" " + data + self._newline_code.encode()
        else:
            send_data = (command + self._newline_code).encode()

        # print(f"<= {send_data}")
        self._ser.write(send_data)

        result = await self._result_queue.get()
        if result.startswith("FAIL"):
            error_code = result[5:].strip() if len(result) > 5 else ""
            raise CommandError(error_code)

        response_lines = []
        while not self._response_queue.empty():
            response_lines.append(await self._response_queue.get())

        return "\r\n".join(response_lines)

    async def get_next_result(self):
        return await self._event_queue.get()
