# VRMNXパワーユニットくん

## 概要
「パワーユニットくん」は「[鉄道模型シミュレーターNX](http://www.imagic.co.jp/hobby/products/vrmnx/ "鉄道模型シミュレーターNX")」（VRMNX）で複数の編成とポイントを操作するためのImGuiウィンドウです。  

## ダウンロード
- [powerunit.py](https://raw.githubusercontent.com/CaldiaNX/vrmnx-ugokunndesu/main/powerunit.py)

## 利用方法
レイアウトファイルと同じフォルダ階層に「powerunit.py」ファイルを配置します。  

フォルダ構成：
```
C:\VRMNX（一例）
├ powerunit.py
└ VRMNXレイアウトファイル.vrmnx
```

対象レイアウトのレイアウトスクリプトに以下の★内容を追記します。  

```py
import vrmapi
import powerunit # ★インポート

def vrmevent(obj,ev,param):
    powerunit.vrmevent(obj,ev,param) # ★メイン処理
    if ev == 'init':
        dummy = 1
    elif ev == 'broadcast':
        dummy = 1
    elif ev == 'timer':
        dummy = 1
    elif ev == 'time':
        dummy = 1
    elif ev == 'after':
        dummy = 1
    elif ev == 'frame':
        dummy = 1
    elif ev == 'keydown':
        dummy = 1
```

ファイル読み込みに成功すると、ビューワー起動時のスクリプトログに

```
import パワーユニットくん Ver.1.2
```

が表示されます。

ビュワー起動時に列車とポイントの初期設定を行います。  
下記編成とポイントは操作対象外としてスキップされます。

- ダミー編成
- 頭文字に「dummy」が付くポイント

## 操作説明

![pwunkn12](https://user-images.githubusercontent.com/66538961/109386008-1bb7e500-793b-11eb-8f2e-b59e02f9ac4d.png)

### 編成リスト
- 「編成名」ボタン
  - 押すと編成が[アクティブ](https://vrmcloud.net/nx/script/script/train/SetActive.html)になります。
  - 車両リストの制御対象となります。
  - 表示名称に全角半角が混じる場合はボタンサイズにずれが生じます。
- 「反」ボタン
  - 押すと編成の[進行方向を反転](https://vrmcloud.net/nx/script/script/train/Turn.html)します。
- 「電圧」スライドバー
  - 動かすと編成の[速度(電圧)を変更](https://vrmcloud.net/nx/script/script/train/SetVoltage.html)します。
- 「全灯」チェックボックス
  - 電装系のON/OFFを一括で切り替えます。
- 「音」チェックボックス
  - 音のON/OFFを切り替えます。
- 「扉L」「扉R」チェックボックス
  - 扉を開閉します。
- 「笛」ボタン
  - 列車の[警笛](https://vrmcloud.net/nx/script/script/train/PlayHorn.html)を鳴らします。

### 車両リスト
「編成名ボタン」で選択した編成の車両設定を個別に設定できます。

|列|略称|操作対象|関連関数|
|--|----|--------|--------|
| 1|－|号車        |[GetCarNumber](https://vrmcloud.net/nx/script/script/car/GetCarNumber.html)|
| 2|HL|ヘッドライト|[GetHeadlight](https://vrmcloud.net/nx/script/script/car/GetHeadlight.html) / [SetHeadlight](https://vrmcloud.net/nx/script/script/car/SetHeadlight.html)|
| 3|TL|テールライト|[GetTaillight](https://vrmcloud.net/nx/script/script/car/GetTaillight.html) / [SetTaillight](https://vrmcloud.net/nx/script/script/car/SetTaillight.html)|
| 4|RS|方向幕      |[GetRollsignLight](https://vrmcloud.net/nx/script/script/car/GetRollsignLight.html) / [SetRollsignLight](https://vrmcloud.net/nx/script/script/car/SetRollsignLight.html)|
| 5|LE|LED         |[GetLEDLight](https://vrmcloud.net/nx/script/script/car/GetLEDLight.html) / [SetLEDLight](https://vrmcloud.net/nx/script/script/car/SetLEDLight.html)|
| 6|RL|ルームライト|[GetRoomlight](https://vrmcloud.net/nx/script/script/car/GetRoomlight.html) / [SetRoomlight](https://vrmcloud.net/nx/script/script/car/SetRoomlight.html)|
| 7|CA|運転台室内灯|[GetCabLight](https://vrmcloud.net/nx/script/script/car/GetCabLight.html) / [SetCabLight](https://vrmcloud.net/nx/script/script/car/SetCabLight.html)|
| 8|SC|入換標識灯  |[GetSCIndicator](https://vrmcloud.net/nx/script/script/car/GetSCIndicator.html) / [SetSCIndicator](https://vrmcloud.net/nx/script/script/car/SetSCIndicator.html)|
| 9|EG|EG灯        |[GetEGIndicator](https://vrmcloud.net/nx/script/script/car/GetEGIndicator.html) / [SetEGIndicator](https://vrmcloud.net/nx/script/script/car/SetEGIndicator.html)|
|10|離|切離し      |[SplitTrain](https://vrmcloud.net/nx/script/script/train/SplitTrain.html)|
|11|SM|蒸気機関車煙|[GetSmoke](https://vrmcloud.net/nx/script/script/car/GetSmoke.html) / [SetSmoke](https://vrmcloud.net/nx/script/script/car/SetSmoke.html)|
|12|HM|ヘッドマーク|[GetHeadmarkDisp](https://vrmcloud.net/nx/script/script/car/GetHeadmarkDisp.html) / [SetHeadmarkDisp](https://vrmcloud.net/nx/script/script/car/SetHeadmarkDisp.html) / [GetCountOfHeadmark](https://vrmcloud.net/nx/script/script/car/GetCountOfHeadmark.html)|
|13|PA|パンタグラフ|[GetPantograph](https://vrmcloud.net/nx/script/script/car/GetPantograph.html) / [SetPantograph](https://vrmcloud.net/nx/script/script/car/SetPantograph.html) / [GetCountOfPantograph](https://vrmcloud.net/nx/script/script/car/GetCountOfPantograph.html)|
|14|OP|オプション  |[GetOptionDisp](https://vrmcloud.net/nx/script/script/car/GetOptionDisp.html) / [SetOptionDisp](https://vrmcloud.net/nx/script/script/car/SetOptionDisp.html)|

- 「切り離し」は2両以上の編成で最後尾以外
- 「蒸気機関車煙」は[車輌の種類](https://vrmcloud.net/nx/script/script/car/GetCarType.html)が蒸気機関車(テンダー含む)のみ表示  
- 「ヘッドマーク」と「パンタグラフ」は設定のある車両のみ表示

### センサー情報表示
センサーに以下のコードを記載することで、編成リストに文字をリアルタイム表示することが出来ます。

```py
elif ev == 'catch':
    # 通過列車オブジェクトを定義
    tr = obj.GetTrain()
    # 列車のDict配列を取得
    di = tr.GetDict()
    # 「pw_ats」キーに文字列を定義
    di["pw_ats"] = obj.GetNAME() + " 通過"
```

### ポイントリスト
- 「直/曲」ラジオボタン
  - 選択するとポイントの[分岐方向を変更](https://vrmcloud.net/nx/script/script/point/SetBranch.html)します。

### ウィンドウの非表示
「P」ボタンを押すとウィンドウの表示/非表示を切り替えできます。  
初期表示を変える場合は「_drawEnable」のTrue/Falseを変更して下さい。

## 履歴
- 2021/02/24 v1.2
  - ファイル読み込み成功時のメッセージ変更
  - 連結/切離し対応
  - 信号対応(一部)
- 2021/02/14 v1.0
  - ファイル名を変更
  - 呼び出し方法を変更
  - 車両個別操作に対応
  - ポイントにIDも追加
  - 扉の開閉に対応
  - その他、多数の処理最適化
- 2021/02/13 v0.2 (β版)
  - 名前変更
  - 電圧の隣にkm/h速度を併記。
  - スライドバーに速度をリアルタイム反映。
  - 編成ボタンにSetActiveを追加。
  - 電灯と音スイッチを3種に分離。
  - ポイントの表示順を変更(ポイント名称での表示ずれを抑えるため)
- 2021/02/12 v0.1 (α版)
  - 新規作成
