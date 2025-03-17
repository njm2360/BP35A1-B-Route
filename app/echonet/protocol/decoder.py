from app.echonet.object.classcode import ClassCode, ClassGroupCode

from app.echonet.protocol.eoj import EnetObject

from app.echonet.property.base_property import BaseProperty
from app.echonet.property.home_equipment_device.low_voltage_smart_pm import (
    LowVoltageSmartPm as LVSPM,
)
from app.echonet.property.profile.node_profile import NodeProfile


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
