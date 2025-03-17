import struct
from enum import IntEnum
from datetime import datetime
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

from app.echonet.object.access import Access
from app.echonet.property.base_property import Property


class LowVoltageSmartPm:
    @dataclass
    class BrouteIdentifyNo(Property):
        """B ルート識別番号(0xC0)"""

        manufacture_code: int = 0
        """メーカーコード"""
        free_area: bytes = field(default_factory=lambda: bytes(12))
        """自由領域"""

        def __post_init__(self):
            self.code = 0xC0
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "LowVoltageSmartPm.BrouteIdentifyNo":
            if len(data) != 16:
                raise ValueError(
                    f"Invalid data length: expected 16 bytes, got {len(data)}"
                )
            manufacture_code = int.from_bytes(data[1:4], byteorder="big")
            free_area = data[4:16]
            return cls(manufacture_code, free_area)

        def encode(self) -> bytes:
            manufacture_code_data = (self.manufacture_code or 0).to_bytes(
                3, byteorder="big"
            )
            free_area_data = self.free_area[:12].ljust(12, b"\x00")
            return b"\x00" + manufacture_code_data + free_area_data

    @dataclass
    class OneMinuteCumulativeEnergy(Property):
        """1分積算電力量 (0xD0)"""

        timestamp: datetime = datetime(2000, 1, 1, 0, 0, 0)
        """計測年月日"""
        forward_energy: Optional[int] = None
        """積算電力量計測値(正方向)"""
        reverse_energy: Optional[int] = None
        """積算電力量計測値(逆方向)"""

        def __post_init__(self):
            self.code = 0xD0
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "LowVoltageSmartPm.OneMinuteCumulativeEnergy":
            if len(data) != 15:
                raise ValueError(
                    f"Invalid data length: expected 15 bytes, got {len(data)}"
                )

            year, month, day, hour, minute, second, forward_energy, reverse_energy = (
                struct.unpack(">HBBBBBII", data)
            )
            timestamp = datetime(year, month, day, hour, minute, second)

            forward_energy = None if forward_energy == 0xFFFFFFFE else forward_energy
            reverse_energy = None if reverse_energy == 0xFFFFFFFE else reverse_energy

            return cls(timestamp, forward_energy, reverse_energy)

        def encode(self) -> bytes:
            timestamp_data = struct.pack(
                ">HBBBBB",
                self.timestamp.year,
                self.timestamp.month,
                self.timestamp.day,
                self.timestamp.hour,
                self.timestamp.minute,
                self.timestamp.second,
            )

            forward_energy_data = (
                self.forward_energy if self.forward_energy is not None else 0xFFFFFFFE
            ).to_bytes(4, byteorder="big")
            reverse_energy_data = (
                self.reverse_energy if self.reverse_energy is not None else 0xFFFFFFFE
            ).to_bytes(4, byteorder="big")

            return timestamp_data + forward_energy_data + reverse_energy_data

    @dataclass
    class Coefficient(Property):
        """係数(0xD3)"""

        value: int = 1
        """値"""

        def __post_init__(self):
            self.code = 0xD3
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "LowVoltageSmartPm.Coefficient":
            if len(data) != 4:
                raise ValueError(
                    f"Invalid data length: expected 4 bytes, got {len(data)}"
                )
            return cls(struct.unpack(">I", data)[0])

        def encode(self) -> bytes:
            return struct.pack(">I", self.value)

    @dataclass
    class CumulativeEnergySignificantDigit(Property):
        """積算電力量有効桁数(0xD7)"""

        value: int = 6
        """桁数"""

        def __post_init__(self):
            self.code = 0xD7
            self.access_rules = [Access.GET]

        @classmethod
        def decode(
            cls, data: bytes
        ) -> "LowVoltageSmartPm.CumulativeEnergySignificantDigit":
            if len(data) != 1:
                raise ValueError(
                    f"Invalid data length: expected 1 byte, got {len(data)}"
                )
            return cls(data[0])

        def encode(self) -> bytes:
            return struct.pack(">B", self.value)

    @dataclass
    class CumulativeEnergyMeasurement(Property):
        """積算電力量計測値 基底クラス (0xE0, 0xE4)"""

        value: Optional[int] = None
        """値(kWh)"""

        @classmethod
        def decode(cls, data: bytes) -> "LowVoltageSmartPm.CumulativeEnergyMeasurement":
            if len(data) != 4:
                raise ValueError(
                    f"Invalid data length: expected 4 bytes, got {len(data)}"
                )
            value = struct.unpack(">I", data)[0]
            value = None if value == 0xFFFFFFFE else value
            return cls(value)

        def encode(self) -> bytes:
            value = self.value if self.value is not None else 0xFFFFFFFE
            return struct.pack(">I", value)

    @dataclass
    class CumulativeEnergyMeasurementNormalDir(CumulativeEnergyMeasurement):
        """積算電力量計測値(正方向計測値) (0xE0)"""

        def __post_init__(self):
            self.code = 0xE0
            self.access_rules = [Access.GET]

    @dataclass
    class CumulativeEnergyUnit(Property):
        """積算電力量単位（正方向、逆方向計測値）(0xE1)"""

        class Unit(IntEnum):
            UNIT_1KWH = 0x00  # 1kWh
            UNIT_0_1KWH = 0x01  # 0.1kWh
            UNIT_0_01KWH = 0x02  # 0.01kWh
            UNIT_0_001KWH = 0x03  # 0.001kWh
            UNIT_0_0001KWH = 0x04  # 0.0001kWh
            UNIT_10KWH = 0x0A  # 10kWh
            UNIT_100KWH = 0x0B  # 100kWh
            UNIT_1000KWH = 0x0C  # 1000kWh
            UNIT_10000KWH = 0x0D  # 10000kWh

        unit: Unit = Unit.UNIT_0_1KWH
        """単位"""

        def __post_init__(self):
            self.code = 0xE1
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "LowVoltageSmartPm.CumulativeEnergyUnit":
            if len(data) != 1:
                raise ValueError(
                    f"Invalid data length: expected 1 byte, got {len(data)}"
                )
            return cls(cls.Unit(data[0]))

        def encode(self) -> bytes:
            return struct.pack(">B", self.unit.value)

    @dataclass
    class CumulativeEnergyMeasurementHistory1(Property):
        """積算電力量計測値履歴１ 基底クラス (0xE2, 0xE4)"""

        collect_day: int = 0
        """積算履歴収集日(0~99)"""
        values: List[int] = field(default_factory=list)
        """計測値(kWh)"""

        @classmethod
        def decode(
            cls, data: bytes
        ) -> "LowVoltageSmartPm.CumulativeEnergyMeasurementHistory1":
            if len(data) != 194:
                raise ValueError(
                    f"Invalid data length: expected 194 bytes, got {len(data)}"
                )
            collect_day = struct.unpack(">H", data[0:2])[0]
            raw_values = list(struct.unpack(">48I", data[2:]))
            values = [None if v == 0xFFFFFFFE else v for v in raw_values]
            return cls(collect_day, values)

        def encode(self) -> bytes:
            collect_day_data = struct.pack(">H", self.collect_day)
            values_data = b"".join(
                struct.pack(">I", v if v is not None else 0xFFFFFFFE)
                for v in self.values
            )
            return collect_day_data + values_data

    @dataclass
    class CumulativeEnergyMeasurementHistory1NormalDir(
        CumulativeEnergyMeasurementHistory1
    ):
        """積算電力量計測値履歴１(正方向計測値) (0xE2)"""

        def __post_init__(self):
            self.code = 0xE2
            self.access_rules = [Access.GET]

    @dataclass
    class CumulativeEnergyMeasurementReverseDir(CumulativeEnergyMeasurement):
        """積算電力量計測値(逆方向計測値) (0xE3)"""

        def __post_init__(self):
            self.code = 0xE3
            self.access_rules = [Access.GET]

    @dataclass
    class CumulativeEnergyMeasurementHistory1ReverseDir(
        CumulativeEnergyMeasurementHistory1
    ):
        """積算電力量計測値履歴１(逆方向計測値) (0xE4)"""

        def __post_init__(self):
            self.code = 0xE4
            self.access_rules = [Access.GET]

    @dataclass
    class CumulativeHistoryCollectDay1(Property):
        """積算履歴収集日１(0xE5)"""

        collect_day: Optional[int] = None
        """収集日(n日前)"""

        def __post_init__(self):
            self.code = 0xE5
            self.access_rules = [Access.GET, Access.SET]

        @classmethod
        def decode(
            cls, data: bytes
        ) -> "LowVoltageSmartPm.CumulativeHistoryCollectDay1":
            if len(data) != 1:
                raise ValueError(
                    f"Invalid data length: expected 1 byte, got {len(data)}"
                )
            return cls(data[0] if data[0] != 0xFF else None)

        def encode(self) -> bytes:
            if self.collect_day is None or not 0 <= self.collect_day <= 99:
                raise ValueError("Day must be between 0 and 99.")
            return struct.pack(">B", self.collect_day)

    @dataclass
    class MomentPower(Property):
        """瞬時電力計測値(0xE7)"""

        value: Optional[int] = None
        """計測値(W)"""

        def __post_init__(self):
            self.code = 0xE7
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "LowVoltageSmartPm.MomentPower":
            if len(data) != 4:
                raise ValueError(
                    f"Invalid data length: expected 4 bytes, got {len(data)}"
                )
            value = struct.unpack(">I", data)[0]
            value = None if value == 0x7FFFFFFE else value
            return cls(value)

        def encode(self) -> bytes:
            value = self.value if self.value is not None else 0x7FFFFFFE
            return struct.pack(">I", value)

    @dataclass
    class MomentCurrent(Property):
        """瞬時電流計測値(0xE8)"""

        r_phase: Optional[float] = None
        """R相電流"""
        t_phase: Optional[float] = None
        """T相電流"""

        def __post_init__(self):
            self.code = 0xE8
            self.access_rules = [Access.GET]

        @classmethod
        def decode(cls, data: bytes) -> "LowVoltageSmartPm.MomentCurrent":
            if len(data) != 4:
                raise ValueError(
                    f"Invalid data length: expected 4 bytes, got {len(data)}"
                )

            r_phase, t_phase = struct.unpack(">HH", data)
            r_phase = None if r_phase == 0x7FFE else r_phase
            t_phase = None if t_phase == 0x7FFE else t_phase

            return cls(r_phase / 10, t_phase / 10)

        def encode(self) -> bytes:
            r_phase_value = (
                int(self.r_phase * 10) if self.r_phase is not None else 0x7FFE
            )
            t_phase_value = (
                int(self.t_phase * 10) if self.t_phase is not None else 0x7FFE
            )

            return struct.pack(">HH", r_phase_value, t_phase_value)

    @dataclass
    class IntCumulativeEnergyMeasurement(Property):
        """定時積算電力量計測値 基底クラス (0xEA, 0xEB)"""

        timestamp: Optional[datetime] = None
        """タイムスタンプ"""
        value: Optional[int] = None
        """積算電力量"""

        @classmethod
        def decode(
            cls, data: bytes
        ) -> "LowVoltageSmartPm.IntCumulativeEnergyMeasurement":
            if len(data) != 11:
                raise ValueError(
                    f"Invalid data length: expected 11 bytes, got {len(data)}"
                )
            year, month, day, hour, minute, second, power = struct.unpack(
                ">HBBBBBI", data
            )
            timestamp = datetime(year, month, day, hour, minute, second)
            power = None if power == 0xFFFFFFFE else power
            return cls(timestamp, power)

        def encode(self) -> list[int]:
            if self.timestamp is None:
                timestamp = datetime.now()
            else:
                timestamp = self.timestamp

            if self.value is None:
                value = 0xFFFFFFFE
            else:
                value = self.value

            return struct.pack(
                ">HBBBBBI",
                timestamp.year,
                timestamp.month,
                timestamp.day,
                timestamp.hour,
                timestamp.minute,
                timestamp.second,
                value,
            )

    @dataclass
    class IntCumulativeEnergyNormalDir(IntCumulativeEnergyMeasurement):
        """定時積算電力量計測値(正方向計測値) (0xEA)"""

        def __post_init__(self):
            self.code = 0xEA
            self.access_rules = [Access.GET]

    @dataclass
    class IntCumulativeEnergyReverseDir(IntCumulativeEnergyMeasurement):
        """定時積算電力量計測値（逆方向計測値） (0xEB)"""

        def __post_init__(self):
            self.code = 0xEB
            self.access_rules = [Access.GET]

    @dataclass
    class CumulativeEnergyMeasurementHistory2(Property):
        """積算電力量計測値履歴２ (0xEC)"""

        timestamp: Optional[datetime] = None
        """積算履歴収集日時"""
        record_count: Optional[int] = None
        """収集コマ数"""
        energy_records: List[Tuple[int, int]] = field(default_factory=list)
        """積算電力量計測値(正方向, 逆方向) (kWh)"""

        def __post_init__(self):
            self.code = 0xEC
            self.access_rules = [Access.GET]

        @classmethod
        def decode(
            cls, data: bytes
        ) -> "LowVoltageSmartPm.CumulativeEnergyMeasurementHistory2":
            if len(data) < 7 or (len(data) - 7) % 8 != 0:
                raise ValueError(
                    f"Invalid data length: expected at least 7 bytes with 8-byte multiples, got {len(data)}"
                )

            year, month, day, hour, minute, record_count = struct.unpack(
                ">HBBBBB", data[:7]
            )
            if (
                year == 0xFFFF
                and month == 0xFF
                and day == 0xFF
                and hour == 0xFF
                and minute == 0xFF
            ):
                return cls(
                    timestamp=None, record_count=1, energy_records=[(None, None)]
                )

            timestamp = datetime(year, month, day, hour, minute)

            records = []
            offset = 7
            for _ in range(record_count):
                if offset + 8 > len(data):
                    raise ValueError(
                        "Insufficient data for the expected number of records"
                    )
                forward_energy, reverse_energy = struct.unpack(
                    ">II", data[offset : offset + 8]
                )

                forward_energy = (
                    None if forward_energy == 0xFFFFFFFE else forward_energy
                )
                reverse_energy = (
                    None if reverse_energy == 0xFFFFFFFE else reverse_energy
                )

                records.append((forward_energy, reverse_energy))
                offset += 8

            return cls(timestamp, record_count, records)

        def encode(self) -> bytes:
            if self.timestamp is None:
                timestamp_data = struct.pack(">HBBBB", 0xFFFF, 0xFF, 0xFF, 0xFF, 0xFF)
            else:
                timestamp_data = struct.pack(
                    ">HBBBB",
                    self.timestamp.year,
                    self.timestamp.month,
                    self.timestamp.day,
                    self.timestamp.hour,
                    self.timestamp.minute,
                )

            record_count_data = struct.pack(">B", self.record_count or 0)
            records_data = b"".join(
                struct.pack(
                    ">II",
                    rec[0] if rec[0] is not None else 0xFFFFFFFE,
                    rec[1] if rec[1] is not None else 0xFFFFFFFE,
                )
                for rec in self.energy_records
            )

            return timestamp_data + record_count_data + records_data

    @dataclass
    class CumulativeHistoryCollectDay2(Property):
        """積算履歴収集日２ (0xED)"""

        timestamp: Optional[datetime] = None
        """積算履歴収集日時 (30分単位)"""
        collect_count: Optional[int] = None
        """収集コマ数"""

        def __post_init__(self):
            self.code = 0xED
            self.access_rules = [Access.GET, Access.SET]

        @classmethod
        def decode(
            cls, data: bytes
        ) -> "LowVoltageSmartPm.CumulativeHistoryCollectDay2":
            if len(data) != 7:
                raise ValueError(
                    f"Invalid data length: expected 7 bytes, got {len(data)}"
                )

            year, month, day, hour, minute, collect_count = struct.unpack(
                ">HBBBBB", data
            )
            if (
                year == 0xFFFF
                and month == 0xFF
                and day == 0xFF
                and hour == 0xFF
                and minute == 0xFF
            ):
                return cls(timestamp=None, collect_count=1)

            timestamp = datetime(year, month, day, hour, minute)

            return cls(timestamp, collect_count)

        def encode(self, mode: Access) -> list[int]:
            if mode == Access.GET:
                return []

            if mode == Access.SET:
                if self.timestamp is None or self.collect_count is None:
                    raise ValueError(
                        "Timestamp and record count must be set for encoding."
                    )
                if self.timestamp.minute not in (0, 30):
                    raise ValueError("Minute must be 00 or 30.")
                if not (1 <= self.collect_count <= 12):
                    raise ValueError("Record count must be between 1 and 12.")

                return list(
                    struct.pack(
                        ">HBBBBB",
                        self.timestamp.year,
                        self.timestamp.month,
                        self.timestamp.day,
                        self.timestamp.hour,
                        self.timestamp.minute,
                        self.collect_count,
                    )
                )

            raise NotImplementedError(f"Encoding for mode {mode} is not implemented")

    @dataclass
    class CumulativeEnergyMeasurementHistory3(Property):
        """積算電力量計測値履歴3 (0xEE)"""

        timestamp: Optional[datetime] = None
        """積算履歴収集日時"""
        record_count: Optional[int] = None
        """収集コマ数 (1～10 コマ)"""
        energy_records: List[Tuple[int, int]] = field(default_factory=list)
        """積算電力量計測値 (正方向, 逆方向) (kWh)"""

        def __post_init__(self):
            self.code = 0xEE
            self.access_rules = [Access.GET]

        @classmethod
        def decode(
            cls, data: bytes
        ) -> "LowVoltageSmartPm.CumulativeEnergyMeasurementHistory3":
            if len(data) < 7 or (len(data) - 7) % 8 != 0:
                raise ValueError(
                    f"Invalid data length: expected at least 7 bytes with 8-byte multiples, got {len(data)}"
                )

            year, month, day, hour, minute, record_count = struct.unpack(
                ">HBBBBB", data[:7]
            )
            if (
                year == 0xFFFF
                and month == 0xFF
                and day == 0xFF
                and hour == 0xFF
                and minute == 0xFF
            ):
                return cls(
                    timestamp=None, record_count=1, energy_records=[(None, None)]
                )

            timestamp = datetime(year, month, day, hour, minute)

            records = []
            offset = 7
            for _ in range(record_count):
                if offset + 8 > len(data):
                    raise ValueError(
                        "Insufficient data for the expected number of records"
                    )
                forward_energy, reverse_energy = struct.unpack(
                    ">II", data[offset : offset + 8]
                )

                forward_energy = (
                    None if forward_energy == 0xFFFFFFFE else forward_energy
                )
                reverse_energy = (
                    None if reverse_energy == 0xFFFFFFFE else reverse_energy
                )

                records.append((forward_energy, reverse_energy))
                offset += 8

            return cls(timestamp, record_count, records)

        def encode(self) -> bytes:
            if self.timestamp is None:
                timestamp_data = struct.pack(">HBBBB", 0xFFFF, 0xFF, 0xFF, 0xFF, 0xFF)
            else:
                timestamp_data = struct.pack(
                    ">HBBBB",
                    self.timestamp.year,
                    self.timestamp.month,
                    self.timestamp.day,
                    self.timestamp.hour,
                    self.timestamp.minute,
                )

            record_count_data = struct.pack(">B", self.record_count or 0)
            records_data = b"".join(
                struct.pack(
                    ">II",
                    rec[0] if rec[0] is not None else 0xFFFFFFFE,
                    rec[1] if rec[1] is not None else 0xFFFFFFFE,
                )
                for rec in self.energy_records
            )

            return timestamp_data + record_count_data + records_data

    @dataclass
    class CumulativeHistoryCollectDay3(Property):
        """積算履歴収集日3 (0xEF)"""

        timestamp: Optional[datetime] = None
        """積算履歴収集日時 (1分単位)"""
        collect_count: Optional[int] = None
        """収集コマ数 (1～10 コマ)"""

        def __post_init__(self):
            self.code = 0xEF
            self.access_rules = [Access.GET, Access.SET]

        @classmethod
        def decode(
            cls, data: bytes
        ) -> "LowVoltageSmartPm.CumulativeHistoryCollectDay3":
            if len(data) != 7:
                raise ValueError(
                    f"Invalid data length: expected 7 bytes, got {len(data)}"
                )

            year, month, day, hour, minute, collect_count = struct.unpack(
                ">HBBBBB", data
            )
            if (
                year == 0xFFFF
                and month == 0xFF
                and day == 0xFF
                and hour == 0xFF
                and minute == 0xFF
            ):
                return cls(timestamp=None, collect_count=1)

            timestamp = datetime(year, month, day, hour, minute)

            return cls(timestamp, collect_count)

        def encode(self) -> bytes:
            if self.timestamp is None or self.collect_count is None:
                raise ValueError("Timestamp and record count must be set for encoding.")
            if not (1 <= self.collect_count <= 10):
                raise ValueError("Record count must be between 1 and 10.")

            return struct.pack(
                ">HBBBBB",
                self.timestamp.year,
                self.timestamp.month,
                self.timestamp.day,
                self.timestamp.hour,
                self.timestamp.minute,
                self.collect_count,
            )
