# -*- coding: utf-8 -*-
"""
VRMNX うごくんです
"""
__author__ = "Caldia"
__status__ = "production"
__version__ = "1.0"
__date__    = "2021/02/12"

import vrmapi

# ファイル読み込みの確認用
vrmapi.LOG("load ugokunndesu.py")

# 編成オブジェクトとポイントオブジェクトに関数で利用する変数を初期設定します
def init():
    #編成リストを新規編成リストに格納
    tList = vrmapi.LAYOUT().GetTrainList()
    #新規編成リストから編成を繰り返し取得
    for tr in tList:
        #ダミーは対象外
        if tr.GetDummyMode() == False:
            setImGuiTrainParam(tr)
        else:
            vrmapi.LOG(tr.GetNAME() + " ダミースキップ")
    #新規ポイントリストを作成
    pList=list()
    #ポイントリストを新規ポイントリストに格納
    vrmapi.LAYOUT().ListPoint(pList)
    #新規ポイントリストからポイントを繰り返し取得
    for pt in pList:
        #setImGuiPointParam(pt)
        #ダミーは対象外(名前判断)
        if pt.GetNAME()[0:5] != 'dummy':
            setImGuiPointParam(pt)
        else:
            vrmapi.LOG(pt.GetNAME() + " ダミースキップ")

# 編成オブジェクト内に表示用タグ作成
def setImGuiTrainParam(tr):
    di = tr.GetDict()
    di['ugoku_vol'] = [tr.GetVoltage()]
    di['ugoku_sw'] = [0]
    # センサー情報を入れるとウィンドウに表示
    di['ugoku_ats'] = ''

# ポイントオブジェクトに表示用タグ作成
def setImGuiPointParam(pt):
    di = pt.GetDict()
    di['ugoku_r'] = [pt.GetBranch()]

# ウィンドウを描画
def drawFrame():
    # ImGui定義
    gui = vrmapi.ImGui()
    gui.Begin("ugoku","うごくんです")
    # 編成リストを新規編成リストに格納
    tList = vrmapi.LAYOUT().GetTrainList()
    # 編成一覧を参照
    for tr in tList:
        if tr.GetDummyMode() == False:
            imguiMakeTrain(gui, tr)
    gui.Separator()
    #ポイントリストを新規ポイントリストに格納
    pList=list()
    vrmapi.LAYOUT().ListPoint(pList)
    #新規ポイントリストからポイントを繰り返し取得
    for pt in pList:
        #ダミーは対象外(名前判断)
        if pt.GetNAME()[0:5] != 'dummy':
            imguiMakePoint(gui, pt)
    gui.End()

# 列車リストを作成します
def imguiMakeTrain(gui, tr):
    # 編成内のパラメータを取得
    di = tr.GetDict()

    # 編成名ボタン(20文字)
    if gui.Button("bt1" + str(tr.GetID()), tr.GetNAME().ljust(20)):
        # 編成操作視点
        vrmapi.LOG(tr.GetNAME() + ".SetView")
        tr.SetView()
    gui.SameLine()

    # 電圧変数取得
    vlary = di['ugoku_vol']
    # 前後ボタン
    if gui.Button('bt3' + str(tr.GetID()), "向"):
        # 方向転換実行
        vrmapi.LOG(tr.GetNAME() + ".Turn")
        tr.Turn()
        # 速度スライドバーを0で再描画
        vlary[0] = 0.0
        gui.SliderFloat('vl' + str(tr.GetID()), '', vlary, 0, 1.0)
    gui.SameLine()

    # スライドバーサイズ調整
    gui.PushItemWidth(100.0)
    # 速度スライドバー
    if gui.SliderFloat('vl' + str(tr.GetID()), '', vlary, 0, 1.0):
        vrmapi.LOG(tr.GetNAME() + ".SetVoltage " + str(round(vlary[0], 2)))
        # 電圧反映
        tr.SetVoltage(vlary[0])
    # サイズリセット
    gui.PopItemWidth()
    gui.SameLine()
    # 速度小数点1桁丸めkm/h表示
    #gui.Text(str(round(tra.GetSpeed(), 1)) + 'km/h')

    # 点灯変数取得
    swary = di['ugoku_sw']
    # 点灯ボタン
    if gui.Checkbox("ch1" + str(tr.GetID()), "灯", swary):
        # 点灯操作
        vrmapi.LOG(tr.GetNAME() + ".setPower " + str(swary[0]))
        setPower(tr, swary[0])
    gui.SameLine()

    # 警笛ボタン
    if gui.Button('bt2' + str(tr.GetID()), "笛"):
        # 警笛実行
        vrmapi.LOG(tr.GetNAME() + ".PlayHorn")
        tr.PlayHorn(0)
    gui.SameLine()

    # センサー位置を表示
    gui.Text(di['ugoku_ats'])

# ポイントリストを作成します
def imguiMakePoint(gui, pt):

    di = pt.GetDict()
    # 名前表示(20文字)
    gui.Text(pt.GetNAME().ljust(20))
    gui.SameLine()

    # ラベル
    gui.Text("直/曲")
    gui.SameLine()

    # 直進用ラジオボタン
    if gui.RadioButton('p0' + str(pt.GetID()), '', di['ugoku_r'], 0):
        pt.SetBranch(0)
        vrmapi.LOG(pt.GetNAME() + ".SetBranch 0")
    gui.SameLine()

    # 曲折用ラジオボタン
    if gui.RadioButton('p1' + str(pt.GetID()), '', di['ugoku_r'], 1):
        pt.SetBranch(1)
        vrmapi.LOG(pt.GetNAME() + ".SetBranch 1")

# 指定編成の車両電装を制御
def setPower(tr, sw):
    # サウンド変更
    if sw == 0:
        # 再生停止
        tr.SetSoundPlayMode(0)
    else:
        # 常時再生
        tr.SetSoundPlayMode(2)
    #車両数を取得
    len = tr.GetNumberOfCars()
    #車両ごとに処理
    for i in range(0, len):
        #ダミーは対象外
        if tr.GetDummyMode():
            vrmapi.LOG(tr.GetNAME() + " ダミースキップ")
        else:
            # 車両を取得
            car = tr.GetCar(i)
            # 方向幕
            car.SetRollsignLight(sw)
            # 室内灯
            car.SetRoomlight(sw)
            # LED
            car.SetLEDLight(sw)
            # 運転台室内灯
            car.SetCabLight(sw)
            # パンダグラフ個数確認
            for j in range(0, car.GetCountOfPantograph()):
                # パンタグラフ
                car.SetPantograph(j,sw)
            # 先頭車両処理(ifを外して中間連結車も含む)
            #if i == 0:
            # ヘッドライト
            car.SetHeadlight(sw)
            # 最後尾車両処理(ifを外して中間連結車も含む)
            #if i == len - 1:
            # テールライト
            car.SetTaillight(sw)
            # 運転台室内灯
            car.SetCabLight(sw)
            # 蒸気機関車用（テンダーも対象）
            if car.GetCarType() == 1:
                # 煙
                car.SetSmoke(sw)