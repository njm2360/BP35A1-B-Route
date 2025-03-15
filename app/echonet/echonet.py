import struct
from typing import Optional
from collections import deque
from datetime import datetime

from app.echonet.rcv_data import EchonetReceiveData
from app.echonet.classcode import ClassCode, ClassGroupCode

from app.echonet.protocol.ehd import EchonetHeader
from app.echonet.protocol.eoj import EnetObject, EnetObjectHeader
from app.echonet.protocol.esv import EnetService
from app.echonet.protocol.access import Access
from app.echonet.property.property import Property

from app.echonet.property.base_property import BaseProperty
from app.echonet.property.home_equipment_device.low_voltage_smart_pm import (
    LowVoltageSmartPm as LVSPM,
)
from app.echonet.property.profile.node_profile import NodeProfile

ECHONET_LITE_PORT = 3610


def getPropertyDecoder(enet_object: EnetObject, epc: int):
    if epc < 0x80:
        raise ValueError("Invalid EPC code")

    # 機器オブジェクトスーパークラス構成プロパティ
    if epc < 0xA0:
        match epc:
            case 0x80:  # 動作状態
                return BaseProperty.OpStatus.decode
            case 0x81:  # 設置場所
                return BaseProperty.InstallLocation.decode
            case 0x82:  # 規格Version情報
                return BaseProperty.VersionInfo.decode
            case 0x83:  # 識別番号
                pass  # return BaseProperty.IdentifierNo.decode # デコーダ未実装
            case 0x84:  # 瞬時消費電力計測値
                return BaseProperty.InstantPowerConsumption.decode
            case 0x85:  # 積算消費電力量計測値
                return BaseProperty.CumulativePowerConsumption.decode
            case 0x86:  # メーカ異常コード
                return BaseProperty.ManufacturerErrorCode.decode
            case 0x87:  # 電流制限設定
                return BaseProperty.CurrentLimitSetting.decode
            case 0x88:  # 異常発生状態
                return BaseProperty.AbnormalState.decode
            case 0x89:  # 異常内容
                pass  # return BaseProperty.AbnormalContent.decode # 複雑なので保留
            case 0x8A:  # 会員ID／メーカコード
                return BaseProperty.MemberID.decode
            case 0x8B:  # 事業場コード
                return BaseProperty.BusinessCode.decode
            case 0x8C:  # 商品コード
                return BaseProperty.ProductCode.decode
            case 0x8D:  # 製造番号
                return BaseProperty.SerialNumber.decode
            case 0x8E:  # 製造年月日
                return BaseProperty.ManufactureDate.decode
            case 0x8F:  # 節電動作設定
                return BaseProperty.PowerSavingMode.decode
            case 0x93:  # 遠隔操作設定
                return BaseProperty.RemoteControlSetting.decode
            case 0x97:  # 現在時刻設定
                return BaseProperty.CurrentTime.decode
            case 0x98:  # 現在年月日設定
                return BaseProperty.CurrentDate.decode
            case 0x99:  # 電力制限設定
                return BaseProperty.PowerLimitSetting.decode
            case 0x9A:  # 積算運転時間
                return BaseProperty.CumulativeOperatingTime.decode
            case 0x9B:  # SetMプロパティマップ
                return BaseProperty.SetMPropertyMap.decode
            case 0x9C:  # GetMプロパティマップ
                return BaseProperty.GetMPropertyMap.decode
            case 0x9D:  # 状変アナウンスプロパティマップ
                return BaseProperty.ChangeAnnoPropertyMap.decode
            case 0x9E:  # Setプロパティマップ
                return BaseProperty.SetPropertyMap.decode
            case 0x9F:  # Getプロパティマップ
                return BaseProperty.GetPropertyMap.decode

    match enet_object.classGroupCode:
        case ClassGroupCode.SensorDevice:
            pass
        case ClassGroupCode.AirConditionerDevice:
            pass
        case ClassGroupCode.HomeEquipmentDevice:
            match enet_object.classCode:
                case ClassCode.LowVoltageSmartPowerMeter:
                    match epc:
                        case 0xC0:  # B ルート識別番号
                            return LVSPM.BrouteIdentifyNo.decode
                        case 0xD0:  # 1分積算電力量計測値（正方向、逆方向計測値）
                            return LVSPM.OneMinuteCumulativeEnergy.decode
                        case 0xD3:  # 係数
                            return LVSPM.Coefficient.decode
                        case 0xD7:  # 積算電力量有効桁数
                            return LVSPM.CumulativeEnergySignificantDigit.decode
                        case 0xE0:  # 積算電力量計測値（正方向計測値）
                            return LVSPM.CumulativeEnergyMeasurementNormalDir.decode
                        case 0xE1:  # 積算電力量単位（正方向、逆方向計測値）
                            return LVSPM.CumulativeEnergyUnit.decode
                        case 0xE2:  # 積算電力量計測値履歴１(正方向計測値)
                            return (
                                LVSPM.CumulativeEnergyMeasurementHistory1NormalDir.decode
                            )
                        case 0xE3:  # 積算電力量計測値(逆方向計測値)
                            return LVSPM.CumulativeEnergyMeasurementReverseDir.decode
                        case 0xE4:  # 積算電力量計測値履歴１(逆方向計測値)
                            return (
                                LVSPM.CumulativeEnergyMeasurementHistory1ReverseDir.decode
                            )
                        case 0xE5:  # 積算履歴収集日１
                            return LVSPM.CumulativeHistoryCollectDay1.decode
                        case 0xE7:  # 瞬時電力計測値
                            return LVSPM.MomentPower.decode
                        case 0xE8:  # 瞬時電流計測値
                            return LVSPM.MomentCurrent.decode
                        case 0xEA:  # 定時積算電力量計測値（正方向計測値）
                            return LVSPM.IntCumulativeEnergyNormalDir.decode
                        case 0xEB:  # 定時積算電力量計測値（逆方向計測値）
                            return LVSPM.IntCumulativeEnergyReverseDir.decode
                        case 0xEC:  # 積算電力量計測値履歴２（正方向、逆方向計測値）
                            return LVSPM.CumulativeEnergyMeasurementHistory2.decode
                        case 0xED:  # 積算履歴収集日２
                            return LVSPM.CumulativeHistoryCollectDay2.decode
                        case 0xEE:  # 積算電力量計測値履歴３（正方向、逆方向計測値）
                            return LVSPM.CumulativeEnergyMeasurementHistory3.decode
                        case 0xEF:  # 積算履歴収集日３
                            return LVSPM.CumulativeHistoryCollectDay3.decode
        case ClassGroupCode.CookingHouseWorkDevice:
            pass
        case ClassGroupCode.HealthDevice:
            pass
        case ClassGroupCode.ManagerOpDevice:
            pass
        case ClassGroupCode.AvDevice:
            pass
        case ClassGroupCode.Profile:
            match enet_object.classCode:
                case ClassCode.NodeProfile:
                    match epc:
                        case 0xBF:  # 個体識別情報
                            pass
                        case 0xD3:  # 自ノードインスタンス数
                            pass
                        case 0xD4:  # 自ノードクラス数
                            pass
                        case 0xD5:  # インスタンスリスト通知
                            return NodeProfile.InstanceListNotify.decode
                        case 0xD6:  # 自ノードインスタンスリストＳ
                            pass
                        case 0xD7:  # 自ノードクラスリストＳ
                            pass
        case ClassGroupCode.UserDefine:
            pass

    print(f"Unsupported ECHONET object")
    print(enet_object, f"EPC: 0x{epc:02X}")


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
        transaction_id=0,  # ToDo デフォルトで持たずに上流で管理するべき
    ):
        self._enet_header = enet_header
        self._transaction_id = transaction_id
        self._enet_object_header = enet_object_header
        self._enet_service = enet_service
        self._properties: deque[Property] = deque()
        self._limitAccessRules = self.ESV_ACCESS_RULES.get(self._enet_service, [])
        self._encode_mode = (
            Access.GET if Access.GET in self._limitAccessRules else Access.SET
        )

    def add(self, property: Property):
        if any(rule in self._limitAccessRules for rule in property.accessRules):
            self._properties.append(property)
        else:
            raise Exception("Access rule violation")

    def make(self) -> bytes:
        result: list[int] = []

        result.extend(self._enet_header.encode())  # EHD
        result.extend(struct.pack(">H", self._transaction_id))  # TID
        result.extend(self._enet_object_header.encode())  # EOJ
        result.append(int(self._enet_service))  # ESV
        result.append(len(self._properties))  # OPC

        while self._properties:
            tx_property = self._properties.popleft()
            tx_data = tx_property.encode(mode=self._encode_mode)

            # ToDo 1232Byte制限はECHONET Lite仕様ではなくBP35A1の仕様、ここに書くべきではない
            if len(result) + len(tx_data) <= 1232:
                result.extend(tx_data)
            else:
                self._properties.appendleft(tx_property)
                break

        self._transaction_id = (self._transaction_id + 1) & 0xFFFF

        return bytes(result)


class ProtocolRx:
    @classmethod
    def proc(cls, data: bytes) -> Optional[EchonetReceiveData]:
        if not cls._is_valid_protocol(data):
            return tuple()

        if len(data) < 12:
            raise ValueError(
                f"Invalid data length: expected at least 12 bytes, got {len(data)}"
            )

        transaction_id = struct.unpack(">H", data[2:4])[0]  # TID
        enet_object_header = EnetObjectHeader.decode(data[4:10])  # EHD
        enet_service = EnetService(data[10])  # ESV
        operation_count = data[11]  # OPC

        # print(
        #     f"TID: {transaction_id}, ESV: 0x{enet_service:02x}, OPC: {operation_count}"
        # )

        properties: list[Property] = []

        if operation_count > 0:
            index = 12

            for _ in range(operation_count):
                if len(data) <= index + 2:
                    raise ValueError("Unexpected end of data while reading EPC and PDC")

                epc, pdc = struct.unpack("BB", data[index : index + 2])
                index += 2

                if pdc == 0:
                    continue

                if len(data) < index + pdc:
                    raise ValueError("Unexpected end of data while reading EDT")

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

        result = EchonetReceiveData(
            received_at=datetime.now(),
            src_enet_object=enet_object_header.src,
            dst_enet_object=enet_object_header.dst,
            enet_service=enet_service,
            transaction_id=transaction_id,
            properties=tuple(properties),
        )

        return result

    @classmethod
    def _is_valid_protocol(cls, data: bytes) -> bool:
        return (
            len(data) >= 2
            and data[0] == EchonetHeader.Header1.ECHONET_LITE
            and data[1] == EchonetHeader.Header2.FORMAT1
        )
