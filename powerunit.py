__title__ = "パワーユニットくん Ver.2.1"
__author__ = "Caldia"
__update__  = "2022/09/10"
__eventUID__ = 1100001

import vrmapi
import os
import json

# ファイル読み込みの確認用
vrmapi.LOG("import " + __title__)
# ウィンドウ描画フラグ
_drawEnable = True
# アクティブ編成オブジェクト
_activeTrainObj = None
# ラジオボタン用
_activeTrainRdo = [0]
# 分岐保存フラグ
_saveSwitchEnable = [0]
_saveSwitchEnable[0] = False

# main
def vrmevent(obj,ev,param):
    global _drawEnable
    if ev == 'init':
        # 初期化
        init()
        # フレームイベント登録
        obj.SetEventFrame()
        # pキー登録
        obj.SetEventKeyDown('P', __eventUID__)
        # 自動ロードを有効にする場合はコメントアウトを外します。
        #loadConfig()
    elif ev == 'frame':
        if _drawEnable:
            # ImGui描画
            drawFrame()
    elif ev == 'keydown':
        # ウィンドウ描画のON/OFF
        if param['keycode'] == 'P' and param['eventUID'] == __eventUID__:
            # 表示反転
            _drawEnable = not _drawEnable


# オブジェクト内に変数初期設定
def init():
    # 編成リストを新規リストに格納
    tList = vrmapi.LAYOUT().GetTrainList()
    # 編成リストから編成を繰り返し取得
    for tr in tList:
        # ダミー編成以外
        if tr.GetDummyMode() == False:
            # 変数初期化
            createDictKey(tr)
            # 編成オブジェクト内に表示用タグ作成
            di = tr.GetDict()
            # 音の初期値を入力
            if tr.GetSoundPlayMode() == 2:
                di['pw_ch2'] = [1]
        else:
            vrmapi.LOG("{0} [{1}] ダミースキップ".format(tr.GetNAME(), tr.GetID()))

    # ポイントリストを新規リストに格納
    pList=list()
    vrmapi.LAYOUT().ListPoint(pList)
    # ポイントリストからポイントを繰り返し取得
    for pt in pList:
        # 頭文字「dummy」は対象外
        if pt.GetNAME()[0:5] != 'dummy':
            # ポイントオブジェクトに表示用タグ作成
            di = pt.GetDict()
            # 初期値設定
            di['pw_r'] = [pt.GetBranch()]
        else:
            vrmapi.LOG("{0} [{1}] ダミースキップ".format(pt.GetNAME(), pt.GetID()))

    # 信号リストを新規リストに格納
    sList=list()
    vrmapi.LAYOUT().ListSignal(sList)
    # ポイントリストからポイントを繰り返し取得
    for sg in sList:
        # 頭文字「dummy」は対象外
        if sg.GetNAME()[0:5] != 'dummy':
            # ポイントオブジェクトに表示用タグ作成
            di = sg.GetDict()
            # 初期値設定
            di['pw_s0'] = [sg.GetStat(0)]
            di['pw_s1'] = [sg.GetStat(1)]
        else:
            vrmapi.LOG("{0} [{1}] ダミースキップ".format(sg.GetNAME(), sg.GetID()))


    # 音源リストを新規リストに格納
    bList=list()
    vrmapi.LAYOUT().ListBell(bList)
    # 音源リストから音源を繰り返し取得
    for bl in bList:
        # 頭文字「dummy」は対象外
        if bl.GetNAME()[0:5] != 'dummy':
            # 音源オブジェクトに表示用タグ作成
            di = bl.GetDict()
            # 初期値設定
            di['pw_b'] = [0]
        else:
            vrmapi.LOG("{0} [{1}] ダミースキップ".format(bl.GetNAME(), bl.GetID()))


# ウィンドウ描画(ツリーを開いている箇所のみ処理してコストを抑える)
def drawFrame():
    global __title__
    # ImGui定義
    gui = vrmapi.ImGui()
    gui.Begin("powerunit", __title__)

    if gui.TreeNode("pwtrain", "編成リスト"):
        # 編成リストを新規編成リストに格納
        tList = vrmapi.LAYOUT().GetTrainList()
        # 編成一覧を参照
        for tr in tList:
            # ダミー編成以外
            if tr.GetDummyMode() == False:
                # 車両数が0以上(連結消失で発生)
                if len(tr.GetCarList()) > 0:
                    imguiMakeTrain(gui, tr)
        gui.TreePop()
    gui.Separator()

    # アクティブ編成が選択されている、かつ0車両以上
    global _activeTrainObj
    if _activeTrainObj is not None and len(_activeTrainObj.GetCarList()) > 0:
        if gui.TreeNode("pwcar", "車両設定 {0} [{1}] {2}".format(_activeTrainObj.GetNAME(), _activeTrainObj.GetID(), _activeTrainObj.GetTrainNumber())):
            # 車両ごとに処理
            for car in _activeTrainObj.GetCarList():
                imguiMakeCar(gui, car)
            gui.Text("HL：ヘッドライト　TL：テールライト　幕：方向幕灯　　　LE：LED 　　　　　RL：ルームライト　CA：運転台室内灯")
            gui.Text("SC：入換標識灯　　EG：EG灯　　　　　煙：蒸気機関車煙　HM：ヘッドマーク　PA：パンタグラフ　OP：オプション　　離：切り離し")
            gui.TreePop()
        gui.Separator()
        if gui.TreeNode("pwwave", "車両音源"):
            imguiMakeSound(gui, _activeTrainObj)
            gui.TreePop()
        gui.Separator()

    if gui.TreeNode("pwpoint", "ポイントリスト"):
        # ポイントリストを取得
        pList=list()
        vrmapi.LAYOUT().ListPoint(pList)
        # ポイント一覧を参照
        gui.Text(" 直／曲  ポイント名 [ID]")
        for pt in pList:
            # ダミーは対象外(名前判断)
            if pt.GetNAME()[0:5] != 'dummy':
                imguiMakePoint(gui, pt)
        gui.TreePop()
    gui.Separator()

    if gui.TreeNode("pwsignal", "信号リスト"):
        # 信号リストを取得
        sList=list()
        vrmapi.LAYOUT().ListSignal(sList)
        # 信号一覧を参照
        gui.Text(" 信号名 [ID]")
        for sg in sList:
            # ダミーは対象外(名前判断)
            if sg.GetNAME()[0:5] != 'dummy':
                imguiMakeSignal(gui, sg)
        gui.TreePop()
    gui.Separator()

    if gui.TreeNode("pwbell", "音源リスト"):
        # 信号リストを取得
        bList=list()
        vrmapi.LAYOUT().ListBell(bList)
        # 音源一覧を参照
        gui.Text(" 停止/再生  音源名 [ID]")
        for bl in bList:
            # ダミーは対象外(名前判断)
            if bl.GetNAME()[0:5] != 'dummy':
                imguiMakeBell(gui, bl)
        gui.TreePop()
    gui.Separator()

    if gui.TreeNode("pwconfig", "設定保存"):
        # セーブボタン
        if gui.Button('bt_sav', "セーブ"):
            # 状態をjsonファイルへ保存
            saveConfig()
        gui.SameLine()
        # 分岐記録チェックボックス
        global _saveSwitchEnable
        gui.Checkbox('pw_ssf', "分岐情報も保存  ", _saveSwitchEnable)
        # ロードボタン
        if gui.Button('bt_lod', "ロード"):
            # 状態をjsonファイルから読み込み
            loadConfig()
            # ロード後に音源適用
            for tr in tList:
                imguiMakeSound(gui, tr)
        # 注意事項
        gui.Text("車両状態と分岐状態(選択可)をjsonファイルへ出力します。")
        gui.Text("車両編成の更新がある場合、エラーとなる可能性があります。")
        gui.Text("ご利用にはご注意ください。")
        gui.TreePop()
    gui.End()


# 状態をjsonファイルへ保存
def saveConfig():
    # ファイルパス有効確認
    path = os.path.splitext(vrmapi.SYSTEM().GetLayoutPath())[0] + '_pw.json'
    if len(path) == 0:
        vrmapi.LOG("ファイル名を定義できません。レイアウトファイルを保存してください。")
        return
    # 保存用Dict
    saveDic = {}
    # 列車用Dict
    tListDic = {}
    # 編成リストを新規編成リストに格納
    tList = vrmapi.LAYOUT().GetTrainList()
    # 編成一覧を参照
    for tr in tList:
        di = tr.GetDict()
        # パワーユニット要素あり(音源Dictで探索)
        if 'pw_wav_car' in di:
            # 車両ステータスリスト
            carli = []
            carwv = []
            # 車両ごとに処理
            for car in tr.GetCarList():
                li = []
                li.append(car.GetHeadlight())
                li.append(car.GetTaillight())
                li.append(car.GetRollsignLight())
                li.append(car.GetLEDLight())
                li.append(car.GetRoomlight())
                li.append(car.GetCabLight())
                li.append(car.GetSCIndicator())
                li.append(car.GetEGIndicator())
                if car.GetCarType() == 1:
                    li.append(car.GetSmoke())
                n = car.GetCountOfHeadmark()
                if n > 0:
                    for idx in range(0, n):
                        li.append(car.GetHeadmarkDisp(idx))
                n = car.GetCountOfPantograph()
                if n > 0:
                    for idx in range(0, n):
                        li.append(car.GetPantograph(idx))
                for idx in range(0, 4):
                    li.append(car.GetOptionDisp(idx))
                carli.append(li)
                # 音源用に車両Dict丸ごと格納(ロード時に取捨選択)
                carwv.append(car.GetDict())
            # オブジェクトIDをキーとして格納
            tListDic[tr.GetID()] = [carli, carwv]
        saveDic['TRAIN'] = tListDic

    # 分岐情報も保存
    if _saveSwitchEnable[0]:
        # ポイント用Dict
        pListDic = {}
        # ポイントリストを取得
        pList=list()
        vrmapi.LAYOUT().ListPoint(pList)
        for pt in pList:
            # オブジェクトIDをキーとして格納
            pListDic[pt.GetID()] = pt.GetBranch()
        saveDic['POINT'] = pListDic

    # レイアウト名のjsonファイルへ保存
    with open(path, 'w') as f:
        json.dump(saveDic, f, indent=1)
        vrmapi.LOG(path + " へ設定保存")


# jsonファイルから状態を読み込み
def loadConfig():
    # ファイルチェック
    path = os.path.splitext(vrmapi.SYSTEM().GetLayoutPath())[0] + '_pw.json'
    if os.path.isfile(path) == False:
        vrmapi.LOG("前回値ファイルがありません。-> " + path)
        return
    vrmapi.LOG(path + " から設定読み込み")
    # レイアウト名のjsonファイルを読み込み
    loadDic = {}
    with open(path) as f:
        loadDic = json.load(f)
    # 編成リスト
    if 'TRAIN' in loadDic:
        tListDic = loadDic['TRAIN']
        # 編成オブジェクトリスト取得
        tList = vrmapi.LAYOUT().GetTrainList()
        for tr in tList:
            # レイアウト内の編成とオブジェクトIDが一致
            sid = str(tr.GetID())
            if sid in tListDic:
                vrmapi.LOG(f"[{sid}] 編成確認")
                # 車両ごとに処理
                carli = tListDic[sid][0]
                # 編成内の車両リストを繰り返し
                cList = tr.GetCarList()
                for idx, car in enumerate(cList):
                    # 車両数を確認
                    if car.GetCarNumber() <= len(carli):
                        li = carli[idx]
                        # リストの並びはsaveConfigのappend順
                        car.SetHeadlight(li[0])
                        car.SetTaillight(li[1])
                        car.SetRollsignLight(li[2])
                        car.SetLEDLight(li[3])
                        car.SetRoomlight(li[4])
                        car.SetCabLight(li[5])
                        car.SetSCIndicator(li[6])
                        car.SetEGIndicator(li[7])
                        # 【仕様注意】以降は可変のため車両組換え後のエラーを許容
                        n1 = 0
                        if car.GetCarType() == 1:
                            car.SetSmoke(li[8])
                            n1 = 1
                        n2 = car.GetCountOfHeadmark()
                        if n2 > 0:
                            for cnt in range(0, n2):
                                car.SetHeadmarkDisp(cnt, li[8 + n1 + cnt])
                        n3 = car.GetCountOfPantograph()
                        if n3 > 0:
                            for cnt in range(0, n3):
                                car.SetPantograph(cnt, li[8 + n1 + n2 + cnt])
                        for cnt in range(0, 4):
                            car.SetOptionDisp(cnt, li[8 + n1 + n2 + n3 + cnt])
                        # 音源リソースをロード
                        di = car.GetDict()
                        copyWaveDict(di, tListDic[sid][1][idx])
                        # 車両音源を設定
                        setWave(car)
            else:
                vrmapi.LOG(f"[{sid}] 編成未確認")

    # ポイントリスト
    if 'POINT' in loadDic:
        pListDic = loadDic['POINT']
        # ポイントリストを取得
        pList=list()
        vrmapi.LAYOUT().ListPoint(pList)
        for pt in pList:
            # レイアウト内のポイントとオブジェクトIDが一致
            sid = str(pt.GetID())
            if sid in pListDic:
                vrmapi.LOG(f"[{sid}] ポイント確認")
                pt.SetBranch(pListDic[sid])
            else:
                vrmapi.LOG(f"[{sid}] ポイント未確認")


# 必要編成オブジェクト初期作成
def createDictKey(tr):
    trDi = tr.GetDict()
    trDi['pw_ch1'] = [0]
    trDi['pw_ch2'] = [0]
    trDi['pw_drl'] = [0]
    trDi['pw_drr'] = [0]
    trDi['pw_msg'] = ''
    trDi['pw_wav_car'] = [0]
    trDi['pw_wav_car'][0] = 1
    # 音源用
    cList = tr.GetCarList()
    # 編成内の車両リストを繰り返し
    for car in cList:
        carDi = car.GetDict()
        carDi['pw_wav_low'] = [0]
        carDi['pw_wav_hig'] = [0]
        carDi['pw_wav_idl'] = [0]
        carDi['pw_wav_bra'] = [0]
        carDi['pw_wav_die'] = [0]
        carDi['pw_wav_com'] = [0]
        carDi['pw_wav_ho1'] = [0]
        carDi['pw_wav_ho2'] = [0]
        carDi['pw_wav_dc'] = [0]
        carDi['pw_wav_dp'] = [0]
        carDi['pw_wav_g1'] = [0]
        carDi['pw_wav_g2'] = [0]
        carDi['pw_wav_sl1'] = [0]
        carDi['pw_wav_sl2'] = [0]
        carDi['pw_wav_sl3'] = [0]
        carDi['pw_wav_vvv'] = [0]
        carDi['pw_wav_pow'] = [0]


# 編成コントローラを作成
def imguiMakeTrain(gui, tr):
    # 編成ID
    strId = str(tr.GetID())
    # 編成内のパラメータを取得
    di = tr.GetDict()

    # 編成名が無ければ新規生成車両とみなす
    if 'pw_ch1' not in di.keys():
        # 変数初期化
        createDictKey(tr)
        # 音の初期値を入力
        if tr.GetSoundPlayMode() == 2:
            di['pw_ch2'] = [1]
        vrmapi.LOG("[{0}] {1} が検出されました".format(strId, tr.GetNAME()))

    # 編成名ラジオボタン
    global _activeTrainRdo
    if gui.RadioButton("rdo" + strId, '', _activeTrainRdo, tr.GetID()):
        # 編成操作（アクティブ化）
        tr.SetActive()
        tr.SetView()
        # 車両操作対象
        global _activeTrainObj
        _activeTrainObj = tr
    gui.SameLine()

    # 速度スライドバー
    # スライドバーサイズ調整
    gui.PushItemWidth(100.0)
    # 電圧取得
    vlary = [tr.GetVoltage()]
    if gui.SliderFloat('vl' + strId, '', vlary, 0, 1.0):
        # 電圧反映
        tr.SetVoltage(vlary[0])
    # サイズリセット
    gui.PopItemWidth()
    gui.SameLine()
    # 速度小数点1桁丸めkm/h表示
    gui.Text((str(round(tr.GetSpeed(), 1)) + 'km/h').rjust(9))
    gui.SameLine()

    # 反転ボタン
    if gui.Button('bt2' + strId, "反"):
        # 方向転換
        tr.Turn()
    gui.SameLine()

    # 警笛ボタン
    if gui.Button('bt3' + strId, '笛'):
        # 警笛
        tr.PlayHorn(0)
    gui.SameLine()
    gui.Text(" ")
    gui.SameLine()

    # 全点灯
    swary = di['pw_ch1']
    # 点灯チェックボックス
    if gui.Checkbox('ch1' + strId, "全灯 ", swary):
        setPower(tr, swary[0])
    gui.SameLine()

    # サウンド
    swary = di['pw_ch2']
    # 音チェックボックス
    if gui.Checkbox('ch2' + strId, "音 ", swary):
        # 音操作
        setSound(tr, swary[0])
    gui.SameLine()

    # 扉L
    swary = di['pw_drl']
    # 扉Lチェックボックス
    if gui.Checkbox('dr0' + strId, '', swary):
        # 扉L操作
        setDoor(tr, swary[0], 0)
    gui.SameLine()

    # 扉R
    swary = di['pw_drr']
    # 扉Rチェックボックス
    if gui.Checkbox('dr1' + strId, '扉LR ', swary):
        # 扉R操作
        setDoor(tr, swary[0], 1)
    gui.SameLine()

    # 名前表示
    gui.Text("{0} [{1}] {2} {3}両 ".format(tr.GetNAME(), strId, tr.GetTrainNumber() ,len(tr.GetCarList())))
    gui.SameLine()

    # センサーメッセージを表示
    gui.Text(di['pw_msg'])


# 車両個別制御表示
def imguiMakeCar(gui, car):
    # 車両IDを取得
    carId = str(car.GetID())

    # ヘッドライト
    sw = car.GetHeadlight()
    if gui.Checkbox('HL' + carId, 'HL ', [sw]):
        car.SetHeadlight(not bool(sw))
    gui.SameLine()

    # テールライト
    sw = car.GetTaillight()
    if gui.Checkbox('TL' + carId, 'TL ', [sw]):
        car.SetTaillight(not bool(sw))
    gui.SameLine()

    # 方向幕
    sw = car.GetRollsignLight()
    if gui.Checkbox('RS' + carId, "幕 ", [sw]):
        car.SetRollsignLight(not bool(sw))
    gui.SameLine()

    # LED
    sw = car.GetLEDLight()
    if gui.Checkbox('LE' + carId, 'LE ', [sw]):
        car.SetLEDLight(not bool(sw))
    gui.SameLine()

    # 室内灯
    sw = car.GetRoomlight()
    if gui.Checkbox('RL' + carId, 'RL', [sw]):
        car.SetRoomlight(not bool(sw))
    gui.SameLine()

    # 運転台室内灯
    sw = car.GetCabLight()
    if gui.Checkbox('CA' + carId, 'CA ', [sw]):
        car.SetCabLight(not bool(sw))
    gui.SameLine()

    # 入換標識灯
    sw = car.GetSCIndicator()
    if gui.Checkbox('SC' + carId, 'SC ', [sw]):
        car.SetSCIndicator(not bool(sw))
    gui.SameLine()

    # EG灯
    sw = car.GetEGIndicator()
    if gui.Checkbox('EG' + carId, 'EG ', [sw]):
        car.SetEGIndicator(not bool(sw))
    gui.SameLine()

    # 末尾以外かつ2両編成以上
    tr = car.GetTrain()
    if car.GetCarPos() != 2 and len(tr.GetCarList()) > 1:
        # 分割ボタン
        if gui.Button('bc1' + carId, "離"):
            # 車両を切り離し
            tr.SplitTrain(car.GetCarNumber())
        gui.SameLine()

    # 蒸気機関車煙（蒸気機関車のみ、テンダーも対象）
    if car.GetCarType() == 1:
        sw = car.GetSmoke()
        if gui.Checkbox('SM' + carId, "煙 ", [sw]):
            car.SetSmoke(not bool(sw))
        gui.SameLine()

    # ヘッドマーク（適用車両のみ）
    n = car.GetCountOfHeadmark()
    if n > 0:
        gui.Text('HM[')
        gui.SameLine()
        for idx in range(0, n):
            gui.Text(str(idx))
            gui.SameLine()
            sw = car.GetHeadmarkDisp(idx)
            if gui.Checkbox('HN' + str(idx) + carId, '', [sw]):
                car.SetHeadmarkDisp(idx, not bool(sw))
            gui.SameLine()
        gui.Text('] ')
        gui.SameLine()

    # パンタグラフ（適用車両のみ）
    n = car.GetCountOfPantograph()
    if n > 0:
        gui.Text('PA[')
        gui.SameLine()
        for idx in range(0, n):
            gui.Text(str(idx))
            gui.SameLine()
            sw = car.GetPantograph(idx)
            if gui.Checkbox('PA' + str(idx) + carId, '', [sw]):
                car.SetPantograph(idx, not bool(sw))
            gui.SameLine()
        gui.Text('] ')
        gui.SameLine()

    # オプション
    gui.Text('OP[')
    gui.SameLine()
    for idx in range(0, 4):
        gui.Text(str(idx))
        gui.SameLine()
        sw = car.GetOptionDisp(idx)
        if gui.Checkbox('OP' + str(idx) + carId, '', [sw]):
            car.SetOptionDisp(idx, not bool(sw))
        gui.SameLine()
    gui.Text('] ')


# 車両音源設定
def imguiMakeSound(gui, tr):
    trDi = tr.GetDict()
    gui.PushItemWidth(80.0)
    if gui.InputInt('pw_wav_car', f"両目 / {tr.GetNumberOfCars()}両", trDi['pw_wav_car']):
        if trDi['pw_wav_car'][0] <= 0:
            trDi['pw_wav_car'][0] = 1
        elif trDi['pw_wav_car'][0] > tr.GetNumberOfCars():
            trDi['pw_wav_car'][0] = tr.GetNumberOfCars()

    car = tr.GetCar(trDi['pw_wav_car'][0] - 1)
    carDi = car.GetDict()
    gui.InputInt('pw_wav_low', "Low  ", carDi['pw_wav_low'])
    gui.SameLine()
    gui.InputInt('pw_wav_hig', "High ", carDi['pw_wav_hig'])
    gui.SameLine()
    gui.InputInt('pw_wav_idl', "Idle ", carDi['pw_wav_idl'])
    gui.SameLine()
    gui.InputInt('pw_wav_bra', "Brake", carDi['pw_wav_bra'])
    gui.SameLine()
    gui.InputInt('pw_wav_die', "Diesel", carDi['pw_wav_die'])
    gui.SameLine()
    gui.InputInt('pw_wav_com', "ｺﾝﾌﾟﾚｯｻｰ", carDi['pw_wav_com'])
    #gui.SameLine()
    gui.InputInt('pw_wav_ho1', "警笛1", carDi['pw_wav_ho1'])
    gui.SameLine()
    gui.InputInt('pw_wav_ho2', "警笛2", carDi['pw_wav_ho2'])
    gui.SameLine()
    gui.InputInt('pw_wav_dc', "扉閉 ", carDi['pw_wav_dc'])
    gui.SameLine()
    gui.InputInt('pw_wav_dp', "扉開 ", carDi['pw_wav_dp'])
    gui.SameLine()
    gui.InputInt('pw_wav_g1', "Gap1  ", carDi['pw_wav_g1'])
    gui.SameLine()
    gui.InputInt('pw_wav_g2', "Gap2 ", carDi['pw_wav_g2'])
    #gui.SameLine()
    gui.InputInt('pw_wav_sl1', "SL1  ", carDi['pw_wav_sl1'])
    gui.SameLine()
    gui.InputInt('pw_wav_sl2', "SL2  ", carDi['pw_wav_sl2'])
    gui.SameLine()
    gui.InputInt('pw_wav_sl3', "SL3  ", carDi['pw_wav_sl3'])
    gui.SameLine()
    gui.InputInt('pw_wav_vvv', "VVVF ", carDi['pw_wav_vvv'])
    gui.SameLine()
    gui.InputInt('pw_wav_pow', "Power", carDi['pw_wav_pow'])
    gui.PopItemWidth()

    if gui.Button('btwavall', "リソースID全車両一括反映"):
        # 全車両繰り返し
        cList = tr.GetCarList()
        for idxCar in cList:
            # 自分以外
            if car.GetCarNumber() != idxCar.GetCarNumber():
                newCarDi = idxCar.GetDict()
                copyWaveDict(newCarDi, carDi)

        vrmapi.LOG("リソースID全車両一括反映")
    gui.SameLine()

    if gui.Button('btwav', "音源適用"):
        # 全車両繰り返し
        cList = tr.GetCarList()
        for idxCar in cList:
            # 車両音源を設定
            setWave(idxCar)
        vrmapi.LOG("音源適用")


# 多重参照になるため手動コピー必須(deepcopy不可)
def copyWaveDict(newDict, orgDict):
    newDict['pw_wav_low'] = orgDict['pw_wav_low'].copy()
    newDict['pw_wav_hig'] = orgDict['pw_wav_hig'].copy()
    newDict['pw_wav_idl'] = orgDict['pw_wav_idl'].copy()
    newDict['pw_wav_bra'] = orgDict['pw_wav_bra'].copy()
    newDict['pw_wav_die'] = orgDict['pw_wav_die'].copy()
    newDict['pw_wav_com'] = orgDict['pw_wav_com'].copy()
    newDict['pw_wav_ho1'] = orgDict['pw_wav_ho1'].copy()
    newDict['pw_wav_ho2'] = orgDict['pw_wav_ho2'].copy()
    newDict['pw_wav_sl1'] = orgDict['pw_wav_sl1'].copy()
    newDict['pw_wav_sl2'] = orgDict['pw_wav_sl2'].copy()
    newDict['pw_wav_sl3'] = orgDict['pw_wav_sl3'].copy()
    newDict['pw_wav_vvv'] = orgDict['pw_wav_vvv'].copy()
    newDict['pw_wav_pow'] = orgDict['pw_wav_pow'].copy()


# 車両音源を設定
def setWave(car):
    carDi = car.GetDict()
    car.SetWaveLow(carDi['pw_wav_low'][0])
    car.SetWaveHigh(carDi['pw_wav_hig'][0])
    car.SetWaveIdle(carDi['pw_wav_idl'][0])
    car.SetWaveBrake(carDi['pw_wav_bra'][0])
    car.SetWaveDiesel(carDi['pw_wav_die'][0])
    car.SetWaveCompressor(carDi['pw_wav_com'][0])
    car.SetWaveHorn(0, carDi['pw_wav_ho1'][0])
    car.SetWaveHorn(1, carDi['pw_wav_ho2'][0])
    car.SetWaveDoorClose(carDi['pw_wav_dc'][0])
    car.SetWaveDoorOpen(carDi['pw_wav_dp'][0])
    car.SetWaveGap1(carDi['pw_wav_g1'][0])
    car.SetWaveGap2(carDi['pw_wav_g2'][0])
    car.SetWaveSL1(carDi['pw_wav_sl1'][0])
    car.SetWaveSL2(carDi['pw_wav_sl2'][0])
    car.SetWaveSL3(carDi['pw_wav_sl3'][0])
    car.SetWaveVVVF(carDi['pw_wav_vvv'][0])
    car.SetWavePower(carDi['pw_wav_pow'][0])


# 指定編成の点灯を制御
def setPower(tr, sw):
    # 車両数を取得
    len = tr.GetNumberOfCars()
    # 車両繰り返し
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
    di['pw_r'] = [pt.GetBranch()]
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


# 音源リストを作成します
def imguiMakeBell(gui, bl):
    # オブジェクトIDを取得
    strId = str(bl.GetID())
    # 音源内のパラメータを取得
    di = bl.GetDict()
    di['pw_b'] = [bl.IsPlay()]
    # 停止ラジオボタン
    if gui.RadioButton('bells' + strId, '', di['pw_b'], 0):
        bl.Stop()
    gui.SameLine()
    # 再生ラジオボタン
    if gui.RadioButton('bellp' + strId, '', di['pw_b'], 1):
        bl.Play()
    gui.SameLine()
    # 名前表示
    gui.Text("{0} [{1}]".format(bl.GetNAME(), strId))
