from enum import StrEnum


class Command(StrEnum):
    """SKコマンド"""

    SKSREG = "SKSREG"  # 仮想レジスタの内容を表示・設定します。
    SKINFO = "SKINFO"  # 現在の主要な通信設定値を表示します。
    SKSTART = "SKSTART"  # 端末をPAA (PANA 認証サーバ)として動作開始します。
    SKJOIN = "SKJOIN"  # 指定した接続先IPv6 アドレスに対してPaC（PANA 認証クライアント）としてPANA 接続シーケンスを開始します。
    SKREJOIN = "SKREJOIN"  # 現在接続中の相手に対して再認証シーケンスを開始します。
    SKTERM = "SKTERM"  # 現在確立しているPANA セッションの終了を要請します。
    SKSENDTO = "SKSENDTO"  # 指定した宛先にUDP でデータを送信します。
    SKPING = "SKPING"  # 指定したIPv6 アドレス宛てにICMP Echo request を送信します。
    SKSCAN = "SKSCAN"  # 指定したチャネルに対してアクティブスキャンまたはED スキャンを実行します。
    SKREGDEV = "SKREGDEV"  # セキュリティを適用するため、指定したIP アドレスを端末に登録します。
    SKRMDEV = "SKRMDEV"  # 指定したIP アドレスのエントリーをネイバーテーブル、ネイバーキャッシュから強制的に削除します。
    SKSETKEY = "SKSETKEY"  # 指定されたキーインデックスに対する暗号キー(128bit)を、MAC 層セキュリティコンポーネントに登録します。
    SKRMKEY = "SKRMKEY"  # 指定されたキーインデックスに対する暗号キー(128bit)を、MAC 層セキュリティコンポーネントから削除します。
    SKSECENABLE = "SKSECENABLE"  # 指定したIP アドレスに対するMAC 層セキュリティの有効・無効を指定します。
    SKSETPSK = "SKSETPSK"  # PANA 認証に用いるPSK を登録します。
    SKSETPWD = "SKSETPWD"  # 指定したパスワードからPSK を生成して登録します。
    SKSETRBID = "SKSETRBID"  # 指定されたID から各Route-B ID を生成して設定します。
    SKADDNBR = "SKADDNBR"  # 指定したIPv6 アドレスとMAC アドレス(IEEE 64bit)情報を、IP 層のネイバーキャッシュにReachable 状態で登録します。
    SKUDPPORT = "SKUDPPORT"  # UDP の待ち受けポートを指定します。
    SKSAVE = "SKSAVE"  # 現在の仮想レジスタの内容をFLASH メモリに保存します。
    SKLOAD = "SKLOAD"  # FLASH メモリに保存されている仮想レジスタの内容を読み出します。
    SKERASE = "SKERASE"  # レジスタ保存用のFLASH メモリエリアを初期化して、未保存状態に戻します。
    SKVER = "SKVER"  # SKSTACK IP のファームウェアバージョンを表示します。
    SKAPPVER = "SKAPPVER"  # アプリケーションのファームウェアバージョンを表示します。
    SKRESET = "SKRESET"  # プロトコル・スタックの内部状態を初期化します。
    SKTABLE = "SKTABLE"  # SKSTACK IP 内の各種テーブル内容を画面表示します。
    SKDSLEEP = "SKDSLEEP"  # スリープモードに移行します。
    SKRFLO = "SKRFLO"  # 受信時のローカル周波数をLower LocalかUpper Local に設定します。
    SKLL64 = "SKLL64"  # MAC アドレスからIPv6 リンクローカルアドレスへ変換した結果を表示します。
    WOPT = "WOPT"  # ERXUDP のデータ部の表示形式を設定します。
    ROPT = "ROPT"  # WOPT コマンドの設定状態を表示します。
    WUART = "WUART"  # UART 設定（ボーレート、キャラクター間インターバル、フロー制御）を設定します。
    RUART = "RUART"  # WUART コマンドの設定状態を表示します。
