import re
import asyncio
import aioserial
from asyncio import Queue
from enum import StrEnum
from typing import Final, Optional, Union

from app.bp35a1.command import Command
from app.bp35a1.rx_state import RxState
from app.bp35a1.event import Epan, Event, EventCode, EventData, RxData
from app.bp35a1.exception import CommandError, PANAConnectError, TxProhibisionError


class BP35A1:
    SERIAL_BAUDRATE: Final[int] = 115200

    AVAIABLE_BAUDRATES: Final[list[int]] = [
        115200,
        2400,
        4800,
        9600,
        19200,
        38400,
        57600,
    ]

    class NewLineCode(StrEnum):
        CRLF = "\r\n"
        CR = "\r"

    def __init__(self, port: str):
        self._ser = aioserial.AioSerial(
            port=port, baudrate=self.SERIAL_BAUDRATE, timeout=3
        )
        self._newline_code = self.NewLineCode.CRLF

        self._buffer = bytearray()
        self._buffer_lock = asyncio.Lock()
        self._rx_state = RxState.NORMAL

        self._event_queue: Queue[Union[EventData]] = Queue()
        self._result_queue: Queue[str] = Queue()
        self._response_queue: Queue[str] = Queue()

        self._udp_tx_allowed: bool = False
        self._rx_task = None

    async def init(self, id: str, password: str):
        if self._rx_task is None:
            self._rx_task = asyncio.create_task(self._proc_rx())

        await self._correct_baudrate()

        await self._send_command(Command.SKRESET, timeout=3, expect_echo=True)
        await self._send_command(Command.SKSREG, ["SFE", "0"], expect_echo=True)

        opt = await self._send_command(Command.ROPT)
        if opt != "01":
            await self._send_command(Command.WOPT, ["01"])

        await self._send_command(Command.SKSETRBID, [id])
        await self._send_command(Command.SKSETPWD, [f"{len(password):X}", password])

    async def _correct_baudrate(self):
        print("Checking baudrate...")

        # タイミングによってはなぜかSKVERがFAILを返すので2回ループ
        for _ in range(2):
            for baudrate in self.AVAIABLE_BAUDRATES:
                try:
                    self._ser.baudrate = baudrate

                    print(f"Testing baudrate {baudrate}bps")

                    await self.clear_buffer()
                    await self._ser.write_async(b"\r\n")
                    self._ser.reset_input_buffer()
                    self._ser.reset_output_buffer()

                    response = await self._send_command(Command.SKVER, expect_echo=True)

                    if response and response.startswith("EVER"):
                        return
                except Exception:
                    pass

        raise Exception("No valid baudrate found.")

    async def scan(self, init_duration: int = 4) -> Optional[Epan]:
        duration = init_duration
        epan = None

        print("Scanning...")

        while duration <= 7:
            await self._send_command(
                Command.SKSCAN,
                ["2", "FFFFFFFF", str(duration)],
            )

            try:
                while True:
                    result = await asyncio.wait_for(self.get_next_result(), timeout=30)
                    if isinstance(result, Epan):
                        epan = result
                    elif isinstance(result, Event):
                        if result.code == EventCode.ACTIVE_SCAN_OK:
                            break
            except asyncio.TimeoutError:
                pass

            if epan:
                return epan

            duration += 1

        return epan

    async def connect(self, epan: Epan) -> str:
        await self._send_command(Command.SKSREG, ["S2", f"{epan.channel:X}"])
        await self._send_command(Command.SKSREG, ["S3", f"{epan.pan_id:X}"])

        ip_address = await self._send_command(Command.SKLL64, [epan.mac_address])

        print("Connecting...")

        await self._send_command(Command.SKJOIN, [ip_address])

        try:
            while True:
                result = await asyncio.wait_for(self.get_next_result(), timeout=30)
                if isinstance(result, Event):
                    if result.code == EventCode.PANA_CONNECT_OK:
                        print(f"PANA connect OK {ip_address}")
                        return ip_address
                    elif result.code == EventCode.PANA_CONNECT_ERROR:
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

        params = [
            f"{handle:X}",
            ip_address,
            f"{port:04X}",
            "1" if security else "2",
            f"{len(data):04X}",
        ]

        await self._send_command(Command.SKSENDTO, params, data)

    async def _proc_rx(self):
        while self._ser.is_open:
            data = await self._ser.read_async()

            if not data:
                continue

            async with self._buffer_lock:
                self._buffer.extend(data)

                if (
                    self._newline_code == self.NewLineCode.CRLF
                    and self._buffer.endswith(b"\r\n")
                ) or (
                    self._newline_code == self.NewLineCode.CR
                    and self._buffer.endswith(b"\r")
                ):
                    line = bytes(self._buffer)
                    self._buffer.clear()

                    asyncio.create_task(self._process_line(line))

    async def _process_line(self, data: bytes):
        # print(f"=> {data}")
        line = data.decode().strip()

        match self._rx_state:
            case RxState.NORMAL:
                if line.startswith("ERXUDP"):  # 4-1
                    datas = line.split(" ")
                    rxdata = RxData(
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
                    self._rx_state = RxState.EPANDESC
                    self._epan = Epan()
                elif line == "EEDSCAN":  # 4-6
                    pass
                elif line == "EPORT":  # 4-7
                    pass
                elif line.startswith("EVENT"):  # 4-8
                    datas = line.split(" ")
                    event = Event(code=EventCode(int(datas[1], 16)), sender=datas[2])

                    match event.code:
                        case EventCode.PANA_CONNECT_OK:
                            self._udp_tx_allowed = True
                        case EventCode.SESITON_LIFETIME_EXPIRE:
                            self._udp_tx_allowed = False

                    await self._event_queue.put(event)
                elif line.startswith("OK") or line.startswith("FAIL"):
                    await self._result_queue.put(line)
                else:
                    await self._response_queue.put(line)
            case RxState.EPANDESC:
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
                        self._rx_state = RxState.NORMAL
                        await self._event_queue.put(self._epan)
            case RxState.SKLL64:
                if not line.startswith("FAIL"):
                    await self._response_queue.put(line)
                    await self._result_queue.put("OK")
                else:
                    await self._result_queue.put(line)
                self._rx_state = RxState.NORMAL
            case RxState.PRODUCT_CONFIG_READ:
                if line.startswith("OK"):
                    datas = line.split(" ", 1)
                    if len(datas) != 2:
                        raise ValueError(
                            "Invalid response. Must be a space-separated string"
                        )
                    await self._response_queue.put(datas[1])
                    await self._result_queue.put(datas[0])
                else:
                    await self._result_queue.put(line)
                self._rx_state = RxState.NORMAL

    async def _send_command(
        self,
        command: Command,
        params: list[str] = [],
        data: bytes = None,
        timeout: float = 1,
        expect_echo: bool = False,
    ) -> Optional[str]:
        self._result_queue = Queue()
        self._response_queue = Queue()

        if command in {Command.WOPT, Command.WUART, Command.ROPT, Command.RUART}:
            self._newline_code = self.NewLineCode.CR
            if command in {Command.ROPT, Command.RUART}:
                self._rx_state = RxState.PRODUCT_CONFIG_READ
        else:
            self._newline_code = self.NewLineCode.CRLF

        if command == Command.SKLL64:
            self._rx_state = RxState.SKLL64

        param_str = f" {' '.join(params)}" if params else ""

        send_data = f"{command.value}{param_str}".encode()

        if data:
            send_data += b" " + data

        send_data += self._newline_code.encode()

        await self._ser.write_async(send_data)
        # print(f"<= {send_data}")

        try:
            if expect_echo:
                await self._skip_echo(command)

            result = await asyncio.wait_for(self._result_queue.get(), timeout=timeout)

            if result.startswith("FAIL"):
                error_code = result[5:].strip() if len(result) > 5 else ""
                raise CommandError(error_code)

            response_lines = []
            while not self._response_queue.empty():
                response_lines.append(await self._response_queue.get())

            return "\r\n".join(response_lines) if response_lines else None
        except asyncio.TimeoutError:
            raise Exception("Result wait timeout")

    async def _skip_echo(self, command: str):
        try:
            response = await asyncio.wait_for(self._response_queue.get(), 1)
            if response == command:
                return

            await self._response_queue.put(response)
        except asyncio.TimeoutError:
            pass

    async def get_next_result(self):
        return await self._event_queue.get()

    async def clear_buffer(self):
        async with self._buffer_lock:
            self._buffer.clear()
