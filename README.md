# うごくんですNX

## 概要
「うごくんですNX」は「[鉄道模型シミュレーターNX](http://www.imagic.co.jp/hobby/products/vrmnx/ "鉄道模型シミュレーターNX")」（VRMNX）で複数の編成とポイントを操作できるImGuiウィンドウです。  

## ダウンロード
- [ugokunndesu.py](https://raw.githubusercontent.com/CaldiaNX/vrmnx-ugokunndesu/main/ugokunndesu.py)

## 利用方法
レイアウトファイルと同じフォルダ階層に「ugokunndesu.py」ファイルを配置します。  

フォルダ構成：
```
C:\VRMNX（一例）
├ ugokunndesu.py
└ VRMNXレイアウトファイル.vrmnx
```

対象レイアウトのレイアウトスクリプトに以下の★内容を追記します。  

```py
import vrmapi
import ugokunndesu # ★「うごくんです」をインポート

def vrmevent(obj,ev,param):
    if ev == 'init':
        dummy = 1
        # ★表示用初期設定
        ugokunndesu.init()
        # ★UID=101でフレームイベントを定義
        obj.SetEventFrame(101)
    elif ev == 'broadcast':
        dummy = 1
    elif ev == 'timer':
        dummy = 1
    elif ev == 'time':
        dummy = 1
    elif ev == 'after':
        dummy = 1
    elif ev == 'frame':
        # ★UID=101で実行
        if param['eventUID'] == 101:
            # ★フレーム毎描画
            ugokunndesu.drawFrame()
    elif ev == 'keydown':
        dummy = 1
```

ファイル読み込みに成功すると、ビューワー起動時のスクリプトログに

```
load ugokunndesu.py
```

が表示されます。   
ビュワー起動時に列車とポイントの初期設定を行います。  
下記編成とポイントは操作対象外としてスキップされます。

- ダミー編成
- 頭文字に「dummy」と付くポイント

## 操作説明

![ugokunndesu](https://user-images.githubusercontent.com/66538961/107662867-110c1780-6cce-11eb-8340-45b4c4fadf5a.png)

### 編成リスト
- 「列車名」ボタン
  - 押すと該当編成がアクティブ（[SetView](https://vrmcloud.net/nx/script/script/train/SetView.html)）になります。
  - 表示名称は半角20文字で設定していますが、全角半角が混じる場合、ボタンサイズにずれが生じます。
- 「向」ボタン
  - 押すと列車の向きを反転（[Turn](https://vrmcloud.net/nx/script/script/train/Turn.html)）します。
- 「電圧」スライドバー
  - 動かすと列車の速度（電圧）を変更（[SetVoltage](https://vrmcloud.net/nx/script/script/train/SetVoltage.html)）します。
- 「灯」チェックボックス
  - 電装系のON/OFFを切り替えます。
- 「笛」ボタン
  - 押すと列車の警笛（[PlayHorn](https://vrmcloud.net/nx/script/script/train/PlayHorn.html)）を鳴らします。

### センサー情報表示
センサーに以下のコードを記載することで、編成リストに文字をリアルタイム表示することが出来ます。

```py
elif ev == 'catch':
    # 通過列車オブジェクトを定義
    tr = obj.GetTrain()
    # 列車のDict配列を取得
    di = tr.GetDict()
    # 「ugoku_ats」キーに文字列を定義
    di["ugoku_ats"] = obj.GetNAME() + " 通過"
```

表示例：  
![ugokunndesu_2](https://user-images.githubusercontent.com/66538961/107666651-166b6100-6cd2-11eb-90f5-d53106108c69.png)

### ポイントリスト
- 「直/曲」ラジオボタン
  - 選択するとポイントの分岐方向を変更（[SetBranch](https://vrmcloud.net/nx/script/script/point/SetBranch.html)）します。

## 履歴
- 2021/02/12 v1.0
  - 公開
