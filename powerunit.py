# -*- coding: utf-8 -*-
"""
パワーユニットくん
"""
__author__ = "Caldia"
__status__ = "production"
__version__ = "1.0"
__date__    = "2021/02/14"

import vrmapi

# ファイル読み込みの確認用
vrmapi.LOG("load powerunit.py")

# ウィンドウ描画フラグ
_drawEnable = True
# アクティブ編成オブジェクト
_activeTrainObj = None

# main
def vrmevent(obj,ev,param):
    global _drawEnable
    if ev == 'init':
        #vrmapi.LOG("powerunit init")
        init()
        obj.SetEventFrame(101)
        obj.SetEventKeyDown('P',102)
    elif ev == 'frame':
        if _drawEnable and param['eventUID'] == 101:
            drawFrame()
    elif ev == 'keydown':
        # ウィンドウ描画のON/OFF
        #vrmapi.LOG("ugokunndesu _drawEnable " + str(_drawEnable))
        if param['eventUID'] == 102:
            if _drawEnable:
                _drawEnable = False
            else:
                _drawEnable = True


# オブジェクト内に変数初期設定
def init():
    # 編成リストを新規編成リストに格納
    tList = vrmapi.LAYOUT().GetTrainList()
    # 編成リストから編成を繰り返し取得
    for tr in tList:
        # ダミー編成は対象外
        if tr.GetDummyMode() == False:
            # 編成オブジェクト内に表示用タグ作成
            di = tr.GetDict()
            di['pw_ch1'] = [0]
            di['pw_ch2'] = [0]
            di['pw_ch3'] = [0]
            # 固定サイズの編成名を初期生成
            di['pw_name'] = tr.GetNAME().ljust(16)
            # センサー情報を入れるとウィンドウに表示
            di['pw_ats'] = ''
        else:
            vrmapi.LOG("{0} [{1}] ダミースキップ".format(tr.GetNAME(), tr.GetID()))

    # ポイントリストを新規ポイントリストに格納
    pList=list()
    vrmapi.LAYOUT().ListPoint(pList)
    # ポイントリストからポイントを繰り返し取得
    for pt in pList:
        # 頭文字「dummy」は対象外
        if pt.GetNAME()[0:5] != 'dummy':
            # ポイントオブジェクトに表示用タグ作成
            di = pt.GetDict()
            di['pw_r'] = [pt.GetBranch()]
        else:
            vrmapi.LOG("{0} [{1}] ダミースキップ".format(pt.GetNAME(), pt.GetID()))


# ウィンドウを描画(内部処理コストを抑える)
def drawFrame():
    # ImGui定義
    gui = vrmapi.ImGui()
    gui.Begin("powerunit","パワーユニットくん")

    # 編成リストを新規編成リストに格納
    tList = vrmapi.LAYOUT().GetTrainList()
    # 編成一覧を参照
    for tr in tList:
        # ダミー編成以外
        if tr.GetDummyMode() == False:
            imguiMakeTrain(gui, tr)
    gui.Separator()

    # アクティブ編成が選択されている
    global _activeTrainObj
    if _activeTrainObj is not None:
        gui.Text("{0} [{1}]".format(_activeTrainObj.GetNAME(), _activeTrainObj.GetID()))
        # 車両ごとに処理
        for car in _activeTrainObj.GetCarList():
            imguiMakeCar(gui, car)
        if vrmapi.ImGui().TreeNode("pw_help", "ヘルプ"):
            gui.Text("HL：ヘッドライト　　TL：テールライト　　RS：方向幕　　LE：LED 　　　　　　RL：ルームライト")
            gui.Text("CA：運転台室内灯　　SC：入換標識灯　　　EG：EG灯　　　SM：蒸気機関車煙　　HM：ヘッドマーク")
            gui.Text("PA：パンタグラフ　　OP：オプション")
            gui.TreePop()
    gui.Separator()

    # ポイントリストを取得
    pList=list()
    vrmapi.LAYOUT().ListPoint(pList)
    # ポイント一覧を参照
    gui.Text(" 直／曲  ポイント名 [ID]")
    for pt in pList:
        # ダミーは対象外(名前判断)
        if pt.GetNAME()[0:5] != 'dummy':
            imguiMakePoint(gui, pt)
    gui.End()


# 編成コントローラを作成
def imguiMakeTrain(gui, tr):
    # 編成ID
    strId = str(tr.GetID())
    # 編成内のパラメータを取得
    di = tr.GetDict()

    # 編成名ボタン
    if gui.Button("bt1" + strId, di['pw_name']):
        # 編成操作（アクティブ化）
        #vrmapi.LOG(tr.GetNAME() + ".SetActive")
        tr.SetActive()
        tr.SetView()
        # 車両操作対象
        global _activeTrainObj
        _activeTrainObj = tr
    gui.SameLine()

    # 反転ボタン
    # 電圧取得
    vlary = [tr.GetVoltage()]
    if gui.Button('bt2' + strId, "反"):
        # 方向転換
        tr.Turn()
        #vrmapi.LOG(tr.GetNAME() + ".Turn")
    gui.SameLine()

    # 速度スライドバー
    # スライドバーサイズ調整
    gui.PushItemWidth(100.0)
    if gui.SliderFloat('vl' + strId, '', vlary, 0, 1.0):
        # 電圧反映
        tr.SetVoltage(vlary[0])
        #vrmapi.LOG(tr.GetNAME() + ".SetVoltage " + str(round(vlary[0], 2)))
    # サイズリセット
    gui.PopItemWidth()
    gui.SameLine()
    # 速度小数点1桁丸めkm/h表示
    gui.Text((str(round(tr.GetSpeed(), 1)) + 'km/h').rjust(9))
    gui.SameLine()

    # 全点灯
    gui.Text(" 全灯")
    gui.SameLine()
    swary = di['pw_ch1']
    # 点灯チェックボックス
    if gui.Checkbox('ch1' + strId, '', swary):
        setPower1(tr, swary[0])
        #vrmapi.LOG(tr.GetNAME() + ".setPower1 " + str(swary[0]))
    gui.SameLine()

    # サウンド
    gui.Text(" 音")
    gui.SameLine()
    swary = di['pw_ch2']
    # 音チェックボックス
    if gui.Checkbox('ch2' + strId, '', swary):
        # 点灯操作
        setPower3(tr, swary[0])
        #vrmapi.LOG(tr.GetNAME() + ".setPower3 " + str(swary[0]))
    gui.SameLine()

    # 警笛ボタン
    if gui.Button('bt3' + strId, '笛'):
        # 警笛
        tr.PlayHorn(0)
        #vrmapi.LOG(tr.GetNAME() + ".PlayHorn")
    gui.SameLine()

    # 位置情報を表示
    gui.Text(di['pw_ats'])


# 車両個別制御表示
def imguiMakeCar(gui, car):
    # 車両IDを取得
    carId = str(car.GetID())

    # ヘッドライト
    gui.Text(str(car.GetCarNumber()).rjust(2) + " HL")
    gui.SameLine()
    sw = car.GetHeadlight()
    if gui.Checkbox('HL' + carId, '', [sw]):
        car.SetHeadlight(not bool(sw))
        #vrmapi.LOG("SetHeadlight " + str(sw))
    gui.SameLine()

    # テールライト
    gui.Text(" TL")
    gui.SameLine()
    sw = car.GetTaillight()
    if gui.Checkbox('TL' + carId, '', [sw]):
        car.SetTaillight(not bool(sw))
        #vrmapi.LOG("SetTaillight " + str(sw))
    gui.SameLine()

    # 方向幕
    gui.Text(" RS")
    gui.SameLine()
    sw = car.GetRollsignLight()
    if gui.Checkbox('RS' + carId, '', [sw]):
        car.SetRollsignLight(not bool(sw))
        #vrmapi.LOG("SetRollsignLight " + str(sw))
    gui.SameLine()

    # LED
    gui.Text(" LE")
    gui.SameLine()
    sw = car.GetLEDLight()
    if gui.Checkbox('LE' + carId, '', [sw]):
        car.SetLEDLight(not bool(sw))
        #vrmapi.LOG("SetLEDLight " + str(sw))
    gui.SameLine()

    # 室内灯
    gui.Text(" RL")
    gui.SameLine()
    sw = car.GetRoomlight()
    if gui.Checkbox('RL' + carId, '', [sw]):
        car.SetRoomlight(not bool(sw))
        #vrmapi.LOG("SetRoomlight " + str(sw))
    gui.SameLine()

    # 運転台室内灯
    gui.Text(" CA")
    gui.SameLine()
    sw = car.GetCabLight()
    if gui.Checkbox('CA' + carId, '', [sw]):
        car.SetCabLight(not bool(sw))
        #vrmapi.LOG("SetCabLight " + str(sw))
    gui.SameLine()

    # 入換標識灯
    gui.Text(" SC")
    gui.SameLine()
    sw = car.GetSCIndicator()
    if gui.Checkbox('SC' + carId, '', [sw]):
        car.SetSCIndicator(not bool(sw))
        #vrmapi.LOG("SetSCIndicator " + str(sw))
    gui.SameLine()

    # EG灯
    gui.Text(" EG")
    gui.SameLine()
    sw = car.GetEGIndicator()
    if gui.Checkbox('EG' + carId, '', [sw]):
        car.SetEGIndicator(not bool(sw))
        #vrmapi.LOG("SetEGIndicator " + str(sw))
    gui.SameLine()

    # 蒸気機関車煙（テンダーも対象）
    if car.GetCarType() == 1:
        gui.Text(" SM")
        gui.SameLine()
        sw = car.GetSmoke()
        if gui.Checkbox('SM' + carId, '', [sw]):
            car.SetSmoke(not bool(sw))
            #vrmapi.LOG("SetSmoke " + str(sw))
        gui.SameLine()

    # ヘッドマーク
    n = car.GetCountOfHeadmark()
    if n > 0:
        gui.Text(" HM[")
        gui.SameLine()
        for idx in range(0, n):
            gui.Text(str(idx))
            gui.SameLine()
            sw = car.GetHeadmarkDisp(idx)
            if gui.Checkbox('HN' + str(idx) + carId, '', [sw]):
                car.SetHeadmarkDisp(idx, not bool(sw))
                #vrmapi.LOG("SetHeadmarkDisp " + str(idx) + " " + str(sw))
            gui.SameLine()
        gui.Text("]")
        gui.SameLine()

    # パンタグラフ
    n = car.GetCountOfPantograph()
    if n > 0:
        gui.Text(" PA[")
        gui.SameLine()
        for idx in range(0, n):
            gui.Text(str(idx))
            gui.SameLine()
            sw = car.GetPantograph(idx)
            if gui.Checkbox('PA' + str(idx) + carId, '', [sw]):
                car.SetPantograph(idx, not bool(sw))
                #vrmapi.LOG("SetPantograph " + str(idx) + " " + str(sw))
            gui.SameLine()
        gui.Text("]")
        gui.SameLine()

    # オプション
    gui.Text(" OP[")
    gui.SameLine()
    for idx in range(0, 4):
        gui.Text(str(idx))
        gui.SameLine()
        sw = car.GetOptionDisp(idx)
        if gui.Checkbox('OP' + str(idx) + carId, '', [sw]):
            car.SetOptionDisp(idx, not bool(sw))
            #vrmapi.LOG("SetOptionDisp " + str(idx) + " " + str(sw))
        gui.SameLine()
    gui.Text("]")


# 指定編成の点灯を制御
def setPower1(tr, sw):
    for car in tr.GetCarList():
        # ヘッドライト
        car.SetHeadlight(sw)
        # テールライト
        car.SetTaillight(sw)
        # 方向幕
        car.SetRollsignLight(sw)
        # LED
        car.SetLEDLight(sw)
        # 室内灯
        car.SetRoomlight(sw)
        # 運転台室内灯
        car.SetCabLight(sw)
        # パンダグラフ個数確認
        for j in range(0, car.GetCountOfPantograph()):
            # パンタグラフ
            car.SetPantograph(j,sw)
        # 蒸気機関車用（テンダーも対象）
        if car.GetCarType() == 1:
            # 煙
            car.SetSmoke(sw)


# 指定編成の音を制御
def setPower3(tr, sw):
    # サウンド変更
    if sw == 0:
        # 再生停止
        tr.SetSoundPlayMode(0)
    else:
        # 常時再生
        tr.SetSoundPlayMode(2)


# ポイントリストを作成します
def imguiMakePoint(gui, pt):
    # オブジェクトIDを取得
    strId = str(pt.GetID())
    # ポイント内のパラメータを取得
    di = pt.GetDict()

    # 直進ラジオボタン
    if gui.RadioButton('pr0' + strId, '', di['pw_r'], 0):
        pt.SetBranch(0)
        #vrmapi.LOG(pt.GetNAME() + ".SetBranch 0")
    gui.SameLine()

    # 曲折ラジオボタン
    if gui.RadioButton('pr1' + strId, '', di['pw_r'], 1):
        pt.SetBranch(1)
        #vrmapi.LOG(pt.GetNAME() + ".SetBranch 1")
    gui.SameLine()

    # 名前表示
    gui.Text("{0} [{1}]".format(pt.GetNAME(), strId))
