__title__ = "パワーユニットくん Ver.3.1"
__author__ = "Caldia"
__update__  = "2024/06/09"

import vrmapi
import os
import json
import math

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
# 踏切保存フラグ
#_saveCrossingEnable = [0]
#_saveCrossingEnable[0] = False

# main
def vrmevent(obj,ev,param):
    global _drawEnable
    if ev == 'init':
        # 初期化
        init(obj)
        # フレームイベント登録
        obj.SetEventFrame()
        # pキー登録
        obj.SetEventKeyDown('P')
        # 自動ロードを有効にする場合はコメントアウトを外します。
        #loadConfig()
    elif ev == 'frame':
        if _drawEnable:
            # ImGui描画
            drawFrame(obj)
    elif ev == 'keydown':
        # ウィンドウ描画のON/OFF
        if param['keycode'] == 'P':
            # 表示反転
            _drawEnable = not _drawEnable


# オブジェクト内に変数初期設定
def init(obj):
    # 編成リストを新規リストに格納
    tList = vrmapi.LAYOUT().GetTrainList()
    # 編成リストから繰り返し取得
    tListCount = 0
    for tr in tList:
        # ダミー編成以外
        if tr.GetDummyMode() == False:
            # 変数初期化
            createDictKey(tr)
            # 音の初期値を入力
            di = tr.GetDict()
            if tr.GetSoundPlayMode() == 2:
                di['pw_ch2'] = [1]
            tListCount += 1
        else:
            vrmapi.LOG("{0} [{1}] ダミースキップ".format(tr.GetNAME(), tr.GetID()))

    # レイアウトDict呼出し
    l_di = obj.GetDict()
    # 編成数を記録(増減で連結切り離しを検知)
    l_di['pw_tListCnt'] = tListCount
    # 編成リストを更新(初回)
    UpdateTrainListTxt(tList)

    # ポイントリストを新規リストに格納
    pList=list()
    vrmapi.LAYOUT().ListPoint(pList)
    l_di['pw_pList'] = []
    # ポイントリストから繰り返し取得
    for pt in pList:
        # 頭文字「dummy」は対象外
        if pt.GetNAME()[0:5] != 'dummy':
            # 分岐の初期値設定
            di = pt.GetDict()
            di['pw_r'] = [pt.GetBranch()]
            # リスト追加
            l_di['pw_pList'].append(pt)
        else:
            vrmapi.LOG("{0} [{1}] ダミースキップ".format(pt.GetNAME(), pt.GetID()))

    # 信号リストを新規リストに格納
    sList=list()
    vrmapi.LAYOUT().ListSignal(sList)
    l_di['pw_sList'] = []
    # 信号リストから繰り返し取得
    for sg in sList:
        # 頭文字「dummy」は対象外
        if sg.GetNAME()[0:5] != 'dummy':
            # 点灯の初期値設定
            di = sg.GetDict()
            di['pw_s0'] = [sg.GetStat(0)]
            di['pw_s1'] = [sg.GetStat(1)]
            # リスト追加
            l_di['pw_sList'].append(sg)
        else:
            vrmapi.LOG("{0} [{1}] ダミースキップ".format(sg.GetNAME(), sg.GetID()))

    # 音源リストを新規リストに格納
    bList=list()
    vrmapi.LAYOUT().ListBell(bList)
    l_di['pw_bList'] = []
    # 音源リストから繰り返し取得
    for bl in bList:
        # 頭文字「dummy」は対象外
        if bl.GetNAME()[0:5] != 'dummy':
            # 初期値設定
            di = bl.GetDict()
            di['pw_b'] = [0]
            # リスト追加
            l_di['pw_bList'].append(bl)
        else:
            vrmapi.LOG("{0} [{1}] ダミースキップ".format(bl.GetNAME(), bl.GetID()))

    # 踏切リストを新規リストに格納
    xList=list()
    vrmapi.LAYOUT().ListCrossing(xList)
    l_di['pw_xList'] = []
    l_di['pw_xTag'] = [0]
    l_di['pw_xTagrb'] = [0]
    # 踏切リストから繰り返し取得
    for xs in xList:
        # 頭文字「dummy」は対象外
        if xs.GetNAME()[0:5] != 'dummy':
            # 初期値設定
            di = xs.GetDict()
            di['pw_ass'] = [xs.ResetAutoSignStatus()]
            di['pw_sig'] = [xs.GetCrossingSign()]
            di['pw_sta'] = [xs.GetCrossingStatus()]
            di['pw_tim'] = [xs.GetCrossingTime()]
            # リスト追加
            l_di['pw_xList'].append(xs)
        else:
            vrmapi.LOG("{0} [{1}] ダミースキップ".format(xs.GetNAME(), xs.GetID()))


# ウィンドウ描画(ツリーを開いている箇所のみ処理してコストを抑える)
def drawFrame(obj):
    global __title__
    # ImGui定義
    gui = vrmapi.ImGui()
    gui.Begin("powerunit", __title__)

    if gui.TreeNode("pwtrain", "列車編成"):
        # 編成リストを新規編成リストに格納
        tList = obj.GetTrainList()
        # レイアウトDict呼出し
        l_di = obj.GetDict()
        tListCount = 0
        # 編成一覧を参照
        for tr in tList:
            # ダミー編成以外
            if tr.GetDummyMode() == False:
                # 車両数が0以上(連結消失で発生)
                if len(tr.GetCarList()) > 0:
                    imguiMakeTrain(gui, tr)
                    tListCount += 1
        # 有効編成数を比較
        if l_di['pw_tListCnt'] != tListCount:
            # 増減あれば更新
            UpdateTrainListTxt(tList)
            vrmapi.LOG("編成数が {0} -> {1} に変化しました".format(l_di['pw_tListCnt'], tListCount))
            l_di['pw_tListCnt'] = tListCount
        gui.TreePop()
    gui.Separator()

    # アクティブ編成が選択されている、かつ0車両以上
    global _activeTrainObj
    if _activeTrainObj is not None and len(_activeTrainObj.GetCarList()) > 0:
        if gui.TreeNode("pwcar", "車両操作 {0} [{1}] {2}".format(_activeTrainObj.GetNAME(), _activeTrainObj.GetID(), _activeTrainObj.GetTrainNumber())):
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

    # レイアウトDict呼出し
    l_di = obj.GetDict()

    if gui.TreeNode("pwpoint", "分岐ポイント"):
        # ポイントリストを取得
        pList = l_di['pw_pList']
        # ポイント一覧を参照
        gui.Text(" 直／曲  ポイント名 [ID]")
        for pt in pList:
            imguiMakePoint(gui, pt)
        gui.TreePop()
    gui.Separator()

    if gui.TreeNode("pwsignal", "信号"):
        # 信号リストを取得
        sList = l_di['pw_sList']
        # 信号一覧を参照
        gui.Text(" 信号名 [ID]")
        for sg in sList:
            imguiMakeSignal(gui, sg)
        gui.TreePop()
    gui.Separator()

    if gui.TreeNode("pwbell", "音源"):
        # 音源リストを取得
        bList = l_di['pw_bList']
        # 音源一覧を参照
        gui.Text(" 停／再  音源名 [ID]")
        for bl in bList:
            imguiMakeBell(gui, bl)
        gui.TreePop()
    gui.Separator()

    if gui.TreeNode("pwcross", "踏切(ホームドア)"):
        # 踏切リストを取得
        xList = l_di['pw_xList']
        # 踏切一覧を参照
        gui.Text(" 無 / 開 / 閉   無/→/←/双(開閉時間)  踏切名 [ID]")
        for xs in xList:
            imguiMakeCross(gui, xs)

        # 踏切グループタグ制御
        gui.Text("踏切グループタグ制御(数値のみ入力可能)")
        if gui.RadioButton('xsta_tag0', '', l_di['pw_xTagrb'], 0):
            tagInt = l_di['pw_xTag'][0]
            obj.CrossingGroupCTRL(str(l_di['pw_xTag'][0]), 0)
        gui.SameLine()
        if gui.RadioButton('xsta_tag1', '', l_di['pw_xTagrb'], 1):
            tagInt = l_di['pw_xTag'][0]
            obj.CrossingGroupCTRL(str(tagInt), 1)
        gui.SameLine()
        if gui.RadioButton('xsta_tag2', ' ', l_di['pw_xTagrb'], 2):
            tagInt = l_di['pw_xTag'][0]
            obj.CrossingGroupCTRL(str(tagInt), 2)
        gui.PushItemWidth(118.0)
        gui.SameLine()
        # 踏切タグ名(InputText無いのでIntで代用)
        gui.InputInt("pwcrosstag", '', l_di['pw_xTag'])
        gui.PopItemWidth()

        gui.TreePop()
    gui.Separator()

    if gui.TreeNode("pwconfig", "設定保存"):
        # セーブボタン
        if gui.Button('bt_sav', "セーブ"):
            # 状態をjsonファイルへ保存
            saveConfig()
        gui.SameLine()
        # ロードボタン
        if gui.Button('bt_lod', "ロード"):
            # 状態をjsonファイルから読み込み
            loadConfig()
        gui.SameLine()
        # 分岐記録チェックボックス
        global _saveSwitchEnable
        gui.Checkbox('pw_ssf', "分岐含む", _saveSwitchEnable)
        #gui.SameLine()
        # 踏切記録チェックボックス
        #global _saveCrossingEnable
        #gui.Checkbox('pw_sxf', "踏切含む", _saveCrossingEnable)
        # 注意事項
        gui.Text("車両状態と分岐状態(選択可)をjsonファイルへ出力します。")
        gui.Text("車両編成更新後に古いファイルを読み込むとエラーになる可能性があります。")
        gui.Text("読み込みエラー発生の場合は古いファイルを削除または上書きしてください。")
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
        l_di = vrmapi.LAYOUT().GetDict()
        pList = l_di['pw_pList']
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
    if _saveSwitchEnable[0] and 'POINT' in loadDic:
        pListDic = loadDic['POINT']
        # ポイントリストを取得
        l_di = vrmapi.LAYOUT().GetDict()
        pList = l_di['pw_pList']
        for pt in pList:
            # レイアウト内のポイントとオブジェクトIDが一致
            sid = str(pt.GetID())
            if sid in pListDic:
                vrmapi.LOG(f"[{sid}] ポイント確認")
                pt.SetBranch(pListDic[sid])
            else:
                vrmapi.LOG(f"[{sid}] ポイント未確認")
    else:
        vrmapi.LOG(f"ポイントロードをスキップ")


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
    trDi['pw_txt'] = ''
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


# ダミー除く全編成の基本情報を更新
def UpdateTrainListTxt(tList):
    # 編成リストから繰り返し取得
    for tr in tList:
        # 編成内のパラメータを取得
        di = tr.GetDict()
        # ダミー編成以外
        if tr.GetDummyMode() == False:
            # 全編成基本情報を更新
            di['pw_txt'] = "{0} [{1}] {2} {3}両 {4}mm".format(tr.GetNAME(), tr.GetID(), tr.GetTrainNumber() ,len(tr.GetCarList()), getTrainLength(tr))


# 編成の全長を求める
def getTrainLength(tr):
    car_list = tr.GetCarList()
    # 前輪と後輪の位置と編成長の変数
    pos0 = []
    pos1 = []
    length = 0.0
    # 編成全体を繰り返し
    for car in car_list:
        # 前輪チェック
        pos0 = car.GetTirePosition(0)
        # 1両目の前輪時はスキップ
        if car.GetCarNumber() > 1:
            # 距離計算
            length += math.sqrt((pos1[0] - pos0[0]) ** 2 + (pos1[2] - pos0[2]) ** 2 + (pos1[1] - pos0[1]) ** 2)
        # 確認用
        #vrmapi.LOG("F\t{0}\t{1}\t{2}\t{3}".format(pos0[0], pos0[2], pos0[1], length))
        # 後輪チェック
        pos1 = car.GetTirePosition(1)
        # 距離計算
        length += math.sqrt((pos1[0] - pos0[0]) ** 2 + (pos1[2] - pos0[2]) ** 2 + (pos1[1] - pos0[1]) ** 2)
        # 確認用
        #vrmapi.LOG("R\t{0}\t{1}\t{2}\t{3}".format(pos1[0], pos1[2], pos1[1], length))
    return round(length)


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
    dirInt = tr.GetDirection()
    dirStr = "前"
    if dirInt == -1:
        dirStr = "後"
    gui.Text(dirStr)
    gui.SameLine()
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

    # 描画
    swary = [tr.IsVisible()]
    # 表示チェックボックス
    if gui.Checkbox('vis' + strId, '表示 ', swary):
        # 表示操作
        tr.SetVisible(swary[0])
    gui.SameLine()

    # 編成情報
    gui.Text(di['pw_txt'])
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
    for idx in range(0, 7):
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
    newDict['pw_wav_dc'] = orgDict['pw_wav_dc'].copy()
    newDict['pw_wav_dp'] = orgDict['pw_wav_dp'].copy()
    newDict['pw_wav_g1'] = orgDict['pw_wav_g1'].copy()
    newDict['pw_wav_g2'] = orgDict['pw_wav_g2'].copy()
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


# 踏切リストを作成します
def imguiMakeCross(gui, xs):
    # オブジェクトIDを取得
    strId = str(xs.GetID())
    # パラメータを取得
    di = xs.GetDict()
    di['pw_ass'] = [xs.ResetAutoSignStatus()]
    di['pw_sig'] = [xs.GetCrossingSign()]
    di['pw_sta'] = [xs.GetCrossingStatus()]
    di['pw_tim'] = [xs.GetCrossingTime()]
    # 開閉状態
    if gui.RadioButton('xsta0' + strId, '', di['pw_sta'], 0):
        xs.SetCrossingStatus(0)
    gui.SameLine()
    if gui.RadioButton('xsta1' + strId, '', di['pw_sta'], 1):
        xs.SetCrossingStatus(1)
    gui.SameLine()
    if gui.RadioButton('xsta2' + strId, ' ', di['pw_sta'], 2):
        xs.SetCrossingStatus(2)
    gui.SameLine()
    # 方向表示状態(警報機)
    if di['pw_tim'][0] <= 0:
        if gui.RadioButton('xsig0' + strId, '', di['pw_sig'], 0):
            xs.SetCrossingSign(0)
        gui.SameLine()
        if gui.RadioButton('xsig1' + strId, '', di['pw_sig'], 1):
            xs.SetCrossingSign(1)
        gui.SameLine()
        if gui.RadioButton('xsig2' + strId, '', di['pw_sig'], 2):
            xs.SetCrossingSign(2)
        gui.SameLine()
        if gui.RadioButton('xsig3' + strId, '', di['pw_sig'], 3):
            xs.SetCrossingSign(3)
        gui.SameLine()
    # 開閉時間(遮断機)
    if di['pw_tim'][0] > 0:
        gui.PushItemWidth(70.0)
        if gui.InputFloat('xtim' + strId, '     ', di['pw_tim']):
            xs.SetCrossingTime(di['pw_tim'][0])
        gui.PopItemWidth()
        gui.SameLine()
    # 名前表示
    gui.Text("{0} [{1}]".format(xs.GetNAME(), strId))
