from collections import deque

from app.echonet.classcode import ClassCode, ClassGroupCode

from app.echonet.protocol.ehd import EHD
from app.echonet.protocol.eoj import EOJ
from app.echonet.protocol.esv import ESV
from app.echonet.protocol.access import Access
from app.echonet.property.property import Property

from app.echonet.property.base_property import BaseProperty
from app.echonet.property.home_equipment_device.low_voltage_smart_pm import (
    LowVoltageSmartPm as LVSPM,
)
from app.echonet.property.profile.node_profile import NodeProfile

ECHONET_LITE_PORT = 3610


def getPropertyDecoder(src: EOJ.EnetObj, epc: int):
    if epc < 0x80:
        print("ERROR: 不正なEPCです")

    # 機器オブジェクトスーパークラス構成プロパティ
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

    match src.classGroupCode:
        case ClassGroupCode.SensorDevice:
            pass
        case ClassGroupCode.AirConditionerDevice:
            pass
        case ClassGroupCode.HomeEquipmentDevice:
            match src.classCode:
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
            match src.classCode:
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

    print(f"サポートされていないECHONETオブジェクトです")
    print(src, f"EPC: 0x{epc:02X}")


class ProtocolTx:
    ESV_ACCESS_RULES = {
        ESV.SetI: [Access.SET],
        ESV.SetC: [Access.SET],
        ESV.Get: [Access.GET],
        ESV.Inf_Req: [Access.ANNO],
        ESV.SetGet: [Access.SET, Access.GET],
        ESV.SetRes: [Access.SET],
        ESV.GetRes: [Access.GET],
        ESV.Inf: [Access.ANNO],
        ESV.InfC: [Access.ANNO],
        ESV.InfcRes: [Access.ANNO],
        ESV.SetGetRes: [Access.SET, Access.GET],
        ESV.SetI_Sna: [Access.SET],
        ESV.SetC_Sna: [Access.SET],
        ESV.Get_Sna: [Access.GET],
        ESV.Inf_Sna: [Access.ANNO],
        ESV.SetGet_Sna: [Access.SET, Access.GET],
    }

    def __init__(
        self,
        eoj: EOJ,
        esv: ESV,
        ehd=EHD(ehd1=EHD.EHD1.ECHONET_LITE, ehd2=EHD.EHD2.FORMAT1),
        tid=0x0001,
    ):
        self._ehd = ehd
        self._tid = tid
        self._eoj = eoj
        self._esv = esv
        self._properties: deque[Property] = deque()
        self._limitAccessRules = self.ESV_ACCESS_RULES.get(self._esv, [])
        self._encode_mode = (
            Access.GET if Access.GET in self._limitAccessRules else Access.SET
        )

    def add(self, property: Property):
        if any(rule in self._limitAccessRules for rule in property.accessRules):
            self._properties.append(property)
        else:
            print("アクセスルール違反")

    def make(self) -> bytes:
        if len(self._properties) == 0:
            print("送信するプロパティがありません")
            return bytes()

        result: list[int] = []

        result.extend(self._ehd.encode())
        result.extend(self._tid.to_bytes(2, byteorder="big"))
        result.extend(self._eoj.encode())
        result.append(int(self._esv))
        result.append(len(self._properties))

        while self._properties:
            tx_property = self._properties.popleft()
            tx_data = tx_property.encode(mode=self._encode_mode)

            # ToDo 1232Byte制限はECHONET Lite仕様ではなくBP35A1の仕様、ここに書くべきではない
            if len(result) + len(tx_data) <= 1232:
                result.extend(tx_data)
            else:
                self._properties.appendleft(tx_property)
                break

        self._tid += 0x0001
        if self._tid > 0xFFFF:
            self._tid = 0x0001

        return bytes(result)


class ProtocolRx:
    @classmethod
    def proc(cls, data: bytes) -> tuple[Property]:
        if not cls._is_valid_protocol(data):
            return tuple()

        if len(data) < 12:
            return tuple()

        cls._tid = int.from_bytes(data[2:4], byteorder="big")
        cls._eoj = EOJ.decode(data[4:10])
        cls._esv = ESV(data[10])
        cls._opc = data[11]

        # print(f"TID: {cls._tid}, ESV: 0x{cls._esv:02x}, OPC: {cls._opc}")

        return cls._parse_properties(data, start_index=12)

    @classmethod
    def _is_valid_protocol(cls, data: bytes) -> bool:
        return (
            len(data) >= 2
            and data[0] == EHD.EHD1.ECHONET_LITE
            and data[1] == EHD.EHD2.FORMAT1
        )

    @classmethod
    def _parse_properties(cls, data: bytes, start_index: int) -> tuple[Property]:
        result: list[Property] = []
        index = start_index

        for _ in range(cls._opc):
            if len(data) <= index + 1:
                break

            epc = data[index]
            pdc = data[index + 1]
            index += 2

            if len(data) < index + pdc or pdc == 0:
                break
            # ToDo PDC=0 の際は応答もしくは自端末へのGET要求、どう処理する？

            edt = data[index : index + pdc]
            index += pdc

            decoder = getPropertyDecoder(src=cls._eoj.src, epc=epc)
            if decoder:
                property = decoder(edt)
                result.append(property)

        return tuple(result)
