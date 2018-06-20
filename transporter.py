import sys
from config import colors
from time import sleep
from ArduinoController.arduino_controller import *
from ColorShapeTracker.color_shape_tracker import *
from args import parse_args

""" 輸入球座標，決定出 action code 的邏輯 """
def _reaction_to_ball(x, y, r):
    if x < .4:
        return 1  # 偏畫面左邊就左轉
    elif x > .6:
        return 2  # 偏畫面右邊就右轉
    else:
        return 3  # 介於中間（0.4~0.6）就直行


def _reaction_to_dest(x, y):
    """ 輸入目的地色塊座標，給出 action code 的邏輯 """
    return 0  # TODO: impl


# 主要程式邏輯（抓球、運送）
def main(args):
    # 連接 Arduino 的 Serial（debug 模式時不會真的連接）
    if not args.debug:
        print('[DEBUG]\t透過 tty {} 連接 Arduino ...'.format(args.tty))
        ctrl = ArduinoController(args.tty, args.baud)
    else:
        print('[DEBUG]\t模擬連接 Arduino ...')
        ctrl = ArduinoController(None)

    print('[DEBUG]\t建立追蹤 {} 球的 ColorShapeTracker ...'.format(args.ball))
    [from_hue, to_hue] = colors.BALL_COLOR_HSV_RANGE[args.ball]
    tracker = ColorShapeTracker(0, from_hue, to_hue, CIRCLE)

    # 找球
    print('[DEBUG]\t開始找球')
    catch_count = 0  # 累計送出「夾球」指令的次數，連續 10 次才視為真的夾到球
    while True:
        # tracker 靠 OpenCV 找出的球座標（若有）
        circle = tracker.find_one()

        # 找不到球就蛇行
        if circle is None:
            ctrl.zigzag()
            continue

        x, y, r = circle
        code = _reaction_to_ball(x, y, r)

        ctrl.dispatch(code)
        if tracker.is_target_catchable():  # 球座標在爪子範圍內
            print('[DEBUG]\t夾球(', catch_count, ')')
            ctrl.dispatch(0)  # 「停」
            ctrl.dispatch(5)  # 「夾」
            catch_count += 1
            # 若連續 10 個 frame 都在夾球範圍內，視為已經夾到球了，進入 Stage 3 開始送球
            if catch_count > 10: break
        else:
            # 球離開夾球區域，視為夾球失敗
            if catch_count is not 0:
                catch_count = 0
                ctrl.dispatch(6)  # 「放」
                ctrl.dispatch(4); sleep(2)  # 「後」，倒車 2 秒

        if args.debug: ctrl.print_action(code)

    # 送到目的地
    print('[DEBUG]\t建立追蹤 {} 色塊的 ColorShapeTracker ...'.format(args.dest))
    [from_hue, to_hue] = colors.DEST_COLOR_HSV_RANGE[args.dest]
    tracker = ColorShapeTracker(0, from_hue, to_hue, CONTOUR)

    print('[DEBUG]\t開始送球')
    while True:
        # 透過 OpenCV 找出的目的地顏色方向
        x, y, _, area = tracker.find_one()

        # 找不到球就蛇行
        if not x:
            ctrl.zigzag()
            continue

        code = _reaction_to_dest(x, y)
        ctrl.dispatch(code)


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    print('[DEBUG]\t執行參數：', args)

    main(args)
