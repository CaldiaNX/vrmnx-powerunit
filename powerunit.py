__title__ = "パワーユニットくん Ver.1.5"
__author__ = "Caldia"
__update__  = "2021/05/18"

import vrmapi

# ファイル読み込みの確認用
vrmapi.LOG("import " + __title__)
# ウィンドウ描画フラグ
_drawEnable = True
# アクティブ編成オブジェクト
_activeTrainObj = None
# ラジオボタン用
_activeTrainRdo = [0]

# main
def vrmevent(obj,ev,param):
    global _drawEnable
    if ev == 'init':
        # 初期化
        init()
        # フレームイベント登録
        obj.SetEventFrame()
        # pキー登録
        obj.SetEventKeyDown('P')
    elif ev == 'frame':
        if _drawEnable:
            # ImGui描画
            drawFrame()
    elif ev == 'keydown':
        # ウィンドウ描画のON/OFF
        if param['keycode'] == 'P':
            # 表示反転
            _drawEnable = not _drawEnable


# オブジェクト内に変数初期設定
def init():
    # 編成リストを新規リストに格納
    tList = vrmapi.LAYOUT().GetTrainList()
    # 編成リストから編成を繰り返し取得
    for obj in tList:
        # ダミー編成以外
        if obj.GetDummyMode() == False:
            # 編成オブジェクト内に表示用タグ作成
            di = obj.GetDict()
            di['pw_ch1'] = [0]
            di['pw_ch2'] = [0]
            di['pw_drl'] = [0]
            di['pw_drr'] = [0]
            di['pw_msg'] = ''
            # 音の初期値を入力
            if obj.GetSoundPlayMode() == 2:
                di['pw_ch2'] = [1]
        else:
            vrmapi.LOG("{0} [{1}] ダミースキップ".format(obj.GetNAME(), obj.GetID()))

    # ポイントリストを新規リストに格納
    pList=list()
    vrmapi.LAYOUT().ListPoint(pList)
    # ポイントリストからポイントを繰り返し取得
    for obj in pList:
        # 頭文字「dummy」は対象外
        if obj.GetNAME()[0:5] != 'dummy':
            # ポイントオブジェクトに表示用タグ作成
            di = obj.GetDict()
            # 初期値設定
            di['pw_r'] = [obj.GetBranch()]
        else:
            vrmapi.LOG("{0} [{1}] ダミースキップ".format(obj.GetNAME(), obj.GetID()))


    # 信号リストを新規リストに格納
    sList=list()
    vrmapi.LAYOUT().ListSignal(sList)
    # ポイントリストからポイントを繰り返し取得
    for obj in sList:
        # 頭文字「dummy」は対象外
        if obj.GetNAME()[0:5] != 'dummy':
            # ポイントオブジェクトに表示用タグ作成
            di = obj.GetDict()
            # 初期値設定
            di['pw_s0'] = [obj.GetStat(0)]
            di['pw_s1'] = [obj.GetStat(1)]
        else:
            vrmapi.LOG("{0} [{1}] ダミースキップ".format(obj.GetNAME(), obj.GetID()))

# ウィンドウを描画(内部処理コストを抑える)
def drawFrame():
    global __title__
    # ImGui定義
    gui = vrmapi.ImGui()
    gui.Begin("powerunit", __title__)

    if vrmapi.ImGui().TreeNode("pwtrain", "編成リスト"):
        # 編成リストを新規編成リストに格納
        tList = vrmapi.LAYOUT().GetTrainList()
        # 編成一覧を参照
        for obj in tList:
            # ダミー編成以外
            if obj.GetDummyMode() == False:
                # 車両数が0以上(連結消失で発生)
                if len(obj.GetCarList()) > 0:
                    imguiMakeTrain(gui, obj)
        gui.TreePop()
    gui.Separator()

    # アクティブ編成が選択されている、かつ0車両以上
    global _activeTrainObj
    if _activeTrainObj is not None and len(_activeTrainObj.GetCarList()) > 0:
        if vrmapi.ImGui().TreeNode("pwcar", "{0} [{1}] {2}".format(_activeTrainObj.GetTrainNumber(), _activeTrainObj.GetID(), _activeTrainObj.GetNAME())):
            # 車両ごとに処理
            for obj in _activeTrainObj.GetCarList():
                imguiMakeCar(gui, obj)
            gui.Text("HL：ヘッドライト　TL：テールライト　RS：方向幕　　　　LE：LED 　　　　　RL：ルームライト　CA：運転台室内灯")
            gui.Text("SC：入換標識灯　　EG：EG灯　　　　　SM：蒸気機関車煙　HM：ヘッドマーク　PA：パンタグラフ　OP：オプション　　離：切り離し")
            gui.TreePop()
        gui.Separator()

    if vrmapi.ImGui().TreeNode("pwpoint", "ポイントリスト"):
        # ポイントリストを取得
        pList=list()
        vrmapi.LAYOUT().ListPoint(pList)
        # ポイント一覧を参照
        gui.Text(" 直／曲  ポイント名 [ID]")
        for obj in pList:
            # ダミーは対象外(名前判断)
            if obj.GetNAME()[0:5] != 'dummy':
                imguiMakePoint(gui, obj)
        gui.TreePop()
    gui.Separator()

    if vrmapi.ImGui().TreeNode("pwsignal", "信号リスト"):
        # ポイントリストを取得
        sList=list()
        vrmapi.LAYOUT().ListSignal(sList)
        # 信号一覧を参照
        gui.Text(" 信号名 [ID]")
        for obj in sList:
            # ダミーは対象外(名前判断)
            if obj.GetNAME()[0:5] != 'dummy':
                imguiMakeSignal(gui, obj)
        gui.TreePop()

    gui.End()


# 編成コントローラを作成
def imguiMakeTrain(gui, tr):
    # 編成ID
    strId = str(tr.GetID())
    # 編成内のパラメータを取得
    di = tr.GetDict()

    # 編成名が無ければ新規生成車両とみなす
    if 'pw_ch1' not in di.keys():
        di['pw_ch1'] = [0]
        di['pw_ch2'] = [0]
        di['pw_drl'] = [0]
        di['pw_drr'] = [0]
        di['pw_msg'] = ''
        # 音の初期値を入力
        if obj.GetSoundPlayMode() == 2:
            di['pw_ch2'] = [1]
        vrmapi.LOG("[{0}] {1} が検出されました".format(strId, tr.GetNAME()))

    # 編成名ラジオボタン
    global _activeTrainRdo
    if gui.RadioButton("rdo" + strId, tr.GetTrainNumber(), _activeTrainRdo, tr.GetID()):
        # 編成操作（アクティブ化）
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
    gui.SameLine()

    # 速度スライドバー
    # スライドバーサイズ調整
    gui.PushItemWidth(100.0)
    if gui.SliderFloat('vl' + strId, '', vlary, 0, 1.0):
        # 電圧反映
        tr.SetVoltage(vlary[0])
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
        setPower(tr, swary[0])
    gui.SameLine()

    # サウンド
    gui.Text(" 音")
    gui.SameLine()
    swary = di['pw_ch2']
    # 音チェックボックス
    if gui.Checkbox('ch2' + strId, '', swary):
        # 音操作
        setSound(tr, swary[0])
    gui.SameLine()

    # 扉L
    gui.Text(" 扉LR")
    gui.SameLine()
    swary = di['pw_drl']
    # 扉Lチェックボックス
    if gui.Checkbox('dr0' + strId, '', swary):
        # 扉L操作
        setDoor(tr, swary[0], 0)
    gui.SameLine()

    # 扉R
    #gui.Text("扉R")
    #gui.SameLine()
    swary = di['pw_drr']
    # 扉Rチェックボックス
    if gui.Checkbox('dr1' + strId, '', swary):
        # 扉R操作
        setDoor(tr, swary[0], 1)
    gui.SameLine()

    # 警笛ボタン
    if gui.Button('bt3' + strId, '笛'):
        # 警笛
        tr.PlayHorn(0)
    gui.SameLine()

    # 名前表示
    gui.Text("[{0}] {1} {2}両".format(strId, tr.GetNAME(), len(tr.GetCarList())))
    gui.SameLine()

    # 位置情報を表示
    gui.Text(di['pw_msg'])


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
    gui.SameLine()

    # テールライト
    gui.Text(" TL")
    gui.SameLine()
    sw = car.GetTaillight()
    if gui.Checkbox('TL' + carId, '', [sw]):
        car.SetTaillight(not bool(sw))
    gui.SameLine()

    # 方向幕
    gui.Text(" RS")
    gui.SameLine()
    sw = car.GetRollsignLight()
    if gui.Checkbox('RS' + carId, '', [sw]):
        car.SetRollsignLight(not bool(sw))
    gui.SameLine()

    # LED
    gui.Text(" LE")
    gui.SameLine()
    sw = car.GetLEDLight()
    if gui.Checkbox('LE' + carId, '', [sw]):
        car.SetLEDLight(not bool(sw))
    gui.SameLine()

    # 室内灯
    gui.Text(" RL")
    gui.SameLine()
    sw = car.GetRoomlight()
    if gui.Checkbox('RL' + carId, '', [sw]):
        car.SetRoomlight(not bool(sw))
    gui.SameLine()

    # 運転台室内灯
    gui.Text(" CA")
    gui.SameLine()
    sw = car.GetCabLight()
    if gui.Checkbox('CA' + carId, '', [sw]):
        car.SetCabLight(not bool(sw))
    gui.SameLine()

    # 入換標識灯
    gui.Text(" SC")
    gui.SameLine()
    sw = car.GetSCIndicator()
    if gui.Checkbox('SC' + carId, '', [sw]):
        car.SetSCIndicator(not bool(sw))
    gui.SameLine()

    # EG灯
    gui.Text(" EG")
    gui.SameLine()
    sw = car.GetEGIndicator()
    if gui.Checkbox('EG' + carId, '', [sw]):
        car.SetEGIndicator(not bool(sw))
    gui.SameLine()

    # 末尾以外かつ2両編成以上
    tr = car.GetTrain()
    if car.GetCarPos() != 2 and len(tr.GetCarList()) > 1:
        gui.Text(" ")
        gui.SameLine()
        # 分割ボタン
        if gui.Button('bc1' + carId, "離"):
            # 車両を切り離し
            tr.SplitTrain(car.GetCarNumber())
        gui.SameLine()

    # 蒸気機関車煙（テンダーも対象）
    if car.GetCarType() == 1:
        gui.Text(" SM")
        gui.SameLine()
        sw = car.GetSmoke()
        if gui.Checkbox('SM' + carId, '', [sw]):
            car.SetSmoke(not bool(sw))
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
        gui.SameLine()
    gui.Text("]")


# 指定編成の点灯を制御
def setPower(tr, sw):
    # 車両数を取得
    len = tr.GetNumberOfCars()
    
    for car in tr.GetCarList():
        # 前後灯
        if car.GetCarNumber() == 1 or car.GetCarNumber() == len:
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
def setSound(tr, sw):
    # サウンド変更
    if sw == 0:
        # 再生停止
        tr.SetSoundPlayMode(0)
    else:
        # 常時再生
        tr.SetSoundPlayMode(2)


# ドアの開閉
def setDoor(tr, sw, lr):
    for car in tr.GetCarList():
        # ドア
        if sw == 0:
            car.CloseDoor_Side(lr, False)
        else:
            car.OpenDoor_Side(lr, False)


# ポイントリストを作成します
def imguiMakePoint(gui, pt):
    # オブジェクトIDを取得
    strId = str(pt.GetID())
    # ポイント内のパラメータを取得
    di = pt.GetDict()

    # 直進ラジオボタン
    if gui.RadioButton('pr0' + strId, '', di['pw_r'], 0):
        pt.SetBranch(0)
    gui.SameLine()

    # 曲折ラジオボタン
    if gui.RadioButton('pr1' + strId, '', di['pw_r'], 1):
        pt.SetBranch(1)
    gui.SameLine()

    # 名前表示
    gui.Text("{0} [{1}]".format(pt.GetNAME(), strId))


# 信号リストを作成します
def imguiMakeSignal(gui, sg):
    # オブジェクトIDを取得
    strId = str(sg.GetID())
    # 信号内のパラメータを取得
    di = sg.GetDict()

    for idx in range(0, 7):
        sw = 0
        if di['pw_s0'][0] == [idx]:
            sw = 1
        if gui.RadioButton('sg' + str(idx) + strId, '', di['pw_s0'], idx):
            sg.SetStat(0,idx)
        gui.SameLine()

    # 名前表示
    gui.Text("{0} [{1}]".format(sg.GetNAME(), strId))
