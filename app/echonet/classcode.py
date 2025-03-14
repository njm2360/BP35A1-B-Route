from enum import IntEnum


class ClassGroupCode(IntEnum):
    SensorDevice = 0x00
    """センサ関連機器クラスグループ"""
    AirConditionerDevice = 0x01
    """空調関連機器クラスグループ"""
    HomeEquipmentDevice = 0x02
    """住宅・設備関連機器クラスグループ"""
    CookingHouseWorkDevice = 0x03
    """調理・家事関連機器クラスグループ"""
    HealthDevice = 0x04
    """健康関連機器クラスグループ"""
    ManagerOpDevice = 0x05
    """管理・操作関連機器クラスグループ"""
    AvDevice = 0x06
    """AV関連機器クラスグループ"""
    Profile = 0x0E
    """プロファイルクラスグループ"""
    UserDefine = 0x0F
    """ユーザー定義クラスグループ"""


class ClassCode(IntEnum):
    # ======センサ関連クラスグループ======
    GasLeakSensor = 0x01
    """ガス漏れセンサ"""
    SecuritySensor = 0x02
    """防犯センサ"""
    EmergencyButton = 0x03
    """非常ボタン"""
    EmergencySensor = 0x04
    """救急用センサ"""
    EarthquakeSensor = 0x05
    """地震センサ"""
    LeakageSensor = 0x06
    """漏電センサ"""
    HumanDetectionSensor = 0x07
    """人体検知センサ"""
    VisitorSensor = 0x08
    """来客センサ"""
    CallSensor = 0x09
    """呼び出しセンサ"""
    CondensationSensor = 0x0A
    """結露センサ"""
    AirPollutionSensor = 0x0B
    """空気汚染センサ"""
    OxygenSensor = 0x0C
    """酸素センサ"""
    IlluminanceSensor = 0x0D
    """照度センサ"""
    SoundSensor = 0x0E
    """音センサ"""
    PostingSensor = 0x0F
    """投函センサ"""
    LoadSensor = 0x10
    """重荷センサ"""
    TemperatureSensor = 0x11
    """温度センサ"""
    HumiditySensor = 0x12
    """湿度センサ"""
    RainSensor = 0x13
    """雨センサ"""
    WaterLevelSensor = 0x14
    """水位センサ"""
    BathWaterLevelSensor = 0x15
    """風呂水位センサ"""
    BathHeatingSensor = 0x16
    """風呂沸き上がりセンサ"""
    WaterLeakSensor = 0x17
    """水漏れセンサ"""
    OverflowSensor = 0x18
    """水あふれセンサ"""
    FireSensor = 0x19
    """火災センサ"""
    TobaccoSmokeSensor = 0x1A
    """タバコ煙センサ"""
    CO2Sensor = 0x1B
    """ＣＯ２センサ"""
    GasSensor = 0x1C
    """ガスセンサ"""
    VOCSensor = 0x1D
    """ＶＯＣセンサ"""
    DifferentialPressureSensor = 0x1E
    """差圧センサ"""
    WindSpeedSensor = 0x1F
    """風速センサ"""
    OdorSensor = 0x20
    """臭いセンサ"""
    FlameSensor = 0x21
    """炎センサ"""
    ElectricEnergySensor = 0x22
    """電力量センサ"""
    ElectricCurrentSensor = 0x23
    """電流センサ"""
    WaterFlowRateSensor = 0x25
    """水流量センサ"""
    MicroMotionSensor = 0x26
    """微動センサ"""
    PassageSensor = 0x27
    """通過センサ"""
    BedSensor = 0x28
    """在床センサ"""
    OpenCloseSensor = 0x29
    """開閉センサ"""
    ActivitySensor = 0x2A
    """活動量センサ"""
    HumanPositionSensor = 0x2B
    """人体位置センサ"""
    SnowSensor = 0x2C
    """雪センサ"""
    AtmosphericPressureSensor = 0x2D
    """気圧センサ"""

    # ======空調関連機器クラスグループ======
    HomeAirConditioner = 0x30
    """家庭用エアコン"""
    AirCoolingUnit = 0x31
    """冷風機"""
    ElectricFan = 0x32
    """扇風機"""
    VentilationFan = 0x33
    """換気扇"""
    AirVentilationFan = 0x34
    """空調換気扇"""
    AirPurifier = 0x35
    """空気清浄器"""
    AirCoolingFan = 0x36
    """冷風扇"""
    Circulator = 0x37
    """サーキュレータ"""
    Dehumidifier = 0x38
    """除湿機"""
    Humidifier = 0x39
    """加湿器"""
    CeilingFan = 0x3A
    """天井扇"""
    ElectricKotatsu = 0x3B
    """電気こたつ"""
    ElectricHeatingPad = 0x3C
    """電気あんか"""
    ElectricBlanket = 0x3D
    """電気毛布"""
    Stove = 0x3E
    """ストーブ"""
    PanelHeater = 0x3F
    """パネルヒータ"""
    ElectricCarpet = 0x40
    """電気カーペット"""
    FloorHeater = 0x41
    """フロアヒータ"""
    ElectricHeater = 0x42
    """電気暖房器"""
    FanHeater = 0x43
    """ファンヒータ"""
    BatteryCharger = 0x44
    """充電器"""
    CommercialACHeatStorageUnit = 0x47
    """業務用パッケージエアコン蓄熱ユニット"""
    CommercialFanCoilUnit = 0x48
    """業務用ファンコイルユニット"""
    CommercialCoolingHeatSource = 0x49
    """業務用空調冷熱源(チラー)"""
    CommercialHeatingHeatSource = 0x50
    """業務用空調温熱源(ボイラー)"""
    CommercialAirConditioningVAV = 0x51
    """業務用空調VAV"""
    CommercialAirHandlingUnit = 0x52
    """業務用空調エアハンドリングユニット"""
    UnitCooler = 0x53
    """ユニットクーラー"""
    CommercialCondensingUnit = 0x54
    """業務用コンデンシングユニット"""
    ElectricHeatStorageHeater = 0x55
    """電気蓄熱暖房器"""
    CommercialACIndoorUnit = 0x56
    """業務用パッケージエアコン室内機（設備用除く）"""
    CommercialACOutdoorUnit = 0x57
    """業務用パッケージエアコン室外機（設備用除く）"""
    GasHeatPumpACIndoorUnit = 0x58
    """業務用ガスヒートポンプエアコン室内機"""
    GasHeatPumpACOutdoorUnit = 0x59
    """業務用ガスヒートポンプエアコン室外機"""
    RangeHood = 0x5A
    """レンジフード"""

    # ======住宅・設備関連機器クラスグループ======
    ElectricBlindAwning = 0x60
    """電動ブラインド･日よけ"""
    ElectricShutter = 0x61
    """電動シャッター"""
    ElectricRainDoorShutter = 0x63
    """電動雨戸・シャッター"""
    ElectricGate = 0x64
    """電動ゲート"""
    ElectricWindow = 0x65
    """電動窓"""
    ElectricEntranceDoor = 0x66
    """電動玄関ドア・引戸"""
    GardenSprinkler = 0x67
    """散水器（庭用）"""
    ElectricWaterHeater = 0x6B
    """電気温水器"""
    ElectricBidetToilet = 0x6E
    """電気便座（温水洗浄便座、暖房便座など）"""
    ElectricLock = 0x6F
    """電気錠"""
    InstantWaterHeater = 0x72
    """瞬間式給湯器"""
    BathroomHeaterDryer = 0x73
    """浴室暖房乾燥機"""
    ResidentialSolarPower = 0x79
    """住宅用太陽光発電"""
    ColdHotWaterSource = 0x7A
    """冷温水熱源機"""
    FloorHeating = 0x7B
    """床暖房"""
    FuelCell = 0x7C
    """燃料電池"""
    StorageBattery = 0x7D
    """蓄電池"""
    EVChargerDischarger = 0x7E
    """電気自動車充放電器"""
    EngineCogeneration = 0x7F
    """エンジンコージェネレーション"""
    ElectricEnergyMeter = 0x80
    """電力量メータ"""
    WaterFlowMeter = 0x81
    """水流量メータ"""
    GasMeter = 0x82
    """ガスメータ"""
    LPGasMeter = 0x83
    """LPガスメータ"""
    DistributionBoardMetering = 0x87
    """分電盤メータリング"""
    LowVoltageSmartPowerMeter = 0x88
    """低圧スマート電力量メータ"""
    SmartGasMeter = 0x89
    """スマートガスメータ"""
    HighVoltageSmartPowerMeter = 0x8A
    """高圧スマート電力量メータ"""
    KeroseneMeter = 0x8B
    """灯油メータ"""
    SmartKeroseneMeter = 0x8C
    """スマート灯油メータ"""
    SmartPowerSubMeter = 0x8D
    """スマート電力量サブメータ"""
    DistributedPowerMeter = 0x8E
    """分散型電源電力量メータ"""
    BidirectionalHighVoltageSmartMeter = 0x8F
    """双方向対応高圧スマート電力量メータ"""
    GeneralLighting = 0x90
    """一般照明"""
    SingleFunctionLighting = 0x91
    """単機能照明"""
    SolidStateLighting = 0x92
    """固体発光光源用照明"""
    EmergencyLighting = 0x99
    """非常照明"""
    Buzzer = 0xA0
    """ブザー"""
    EVCharger = 0xA1
    """電気自動車充電器"""
    HouseholdSmallWindTurbine = 0xA2
    """Household small wind turbine power generation"""
    LightingSystem = 0xA3
    """照明システム"""
    ExtendedLightingSystem = 0xA4
    """拡張照明システム"""
    MultiInputPCS = 0xA5
    """マルチ入力PCS"""
    HybridWaterHeater = 0xA6
    """ハイブリッド給湯機"""
    FrequencyControl = 0xA7
    """周波数制御"""

    # ======調理・家事関連機器クラスグループ======
    CoffeeMaker = 0xB0
    """コーヒーメーカ"""
    CoffeeMill = 0xB1
    """コーヒーミル"""
    ElectricPot = 0xB2
    """電気ポット"""
    ElectricCooktop = 0xB3
    """電気こんろ"""
    Toaster = 0xB4
    """トースタ"""
    JuicerMixer = 0xB5
    """ジューサ・ミキサ"""
    FoodProcessor = 0xB6
    """フードプロセッサ"""
    RefrigeratorFreezer = 0xB7
    """冷凍冷蔵庫"""
    OvenMicrowave = 0xB8
    """オーブンレンジ"""
    CookingHeater = 0xB9
    """クッキングヒータ"""
    Oven = 0xBA
    """オーブン"""
    RiceCooker = 0xBB
    """炊飯器"""
    ElectricRiceJar = 0xBC
    """電子ジャー"""
    Dishwasher = 0xBD
    """食器洗い機"""
    DishDryer = 0xBE
    """食器乾燥機"""
    ElectricMochiMaker = 0xBF
    """電気もちつき機"""
    Warmer = 0xC0
    """保温機"""
    RicePolisher = 0xC1
    """精米機"""
    BreadMaker = 0xC2
    """自動製パン機"""
    SlowCooker = 0xC3
    """スロークッカ"""
    ElectricPickleMaker = 0xC4
    """電気漬物機"""
    WashingMachine = 0xC5
    """洗濯機"""
    ClothesDryer = 0xC6
    """衣類乾燥機"""
    ElectricIron = 0xC7
    """電気アイロン"""
    PantsPress = 0xC8
    """ズボンプレッサ"""
    FutonDryer = 0xC9
    """ふとん乾燥機"""
    ShoeDryer = 0xCA
    """小物・くつ乾燥機"""
    VacuumCleaner = 0xCB
    """電気掃除機（セントラルクリーナ含む）"""
    GarbageDisposer = 0xCC
    """ディスポーザ"""
    ElectricMosquitoRepellent = 0xCD
    """電気蚊取り機"""
    CommercialShowcase = 0xCE
    """業務用ショーケース"""
    CommercialRefrigerator = 0xCF
    """業務用冷蔵庫"""
    CommercialHotCase = 0xD0
    """業務用ホットケース"""
    CommercialFryer = 0xD1
    """業務用フライヤー"""
    CommercialMicrowave = 0xD2
    """業務用電子レンジ"""
    WasherDryer = 0xD3
    """洗濯乾燥機"""
    CommercialShowcaseOutdoorUnit = 0xD4
    """業務用ショーケース向け室外機"""
    DishwasherDryer = 0xD5
    """食器洗い乾燥機"""

    # ======健康関連機器クラスグループ======
    WeighingScale = 0x01
    """体重計"""
    Thermometer = 0x02
    """体温計"""
    BloodPressureMonitor = 0x03
    """血圧計"""
    BloodGlucoseMeter = 0x04
    """血糖値計"""
    BodyFatMeter = 0x05
    """体脂肪計"""

    # ======管理・操作関連機器クラスグループ======
    ParallelProcessingPowerControl = 0xFA
    """並列処理併用型電力制御"""
    DREventController = 0xFB
    """DR イベントコントローラ"""
    SecureCommSharedKeyNode = 0xFC
    """セキュア通信用共有鍵設定ノード"""
    SwitchJEMA_HA = 0xFD
    """スイッチ（JEMA/HA 端子対応）"""
    MobileTerminal = 0xFE
    """携帯端末"""
    Controller = 0xFF
    """コントローラ"""

    # ======AV関連機器クラスグループ======
    Display = 0x01
    """ディスプレー"""
    Television = 0x02
    """テレビ"""
    AudioSystem = 0x03
    """オーディオ"""
    NetworkCamera = 0x04
    """ネットワークカメラ"""

    # ========プロファイルクラスグループ=========
    NodeProfile = 0xF0
    """ノードプロファイル"""
