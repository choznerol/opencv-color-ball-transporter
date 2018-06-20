import argparse
from config import colors

description = '''
description:
    以影像辨識（詳見 color_shape_tracker.py）抓取指定顏色的圓球送往指定顏色的區域。透過 Serial 將約
    定好的 action code 傳給 tty device（例：Arduino）進一步控制移動、開合夾爪

    action code 格式：0: 不動, 1: 左轉, 2: 右轉, 3: 前進 , 4: 後退, 5: 關爪子, 6: 開爪
'''

epilog = '''
examples:
    1. 在 RPi 上把藍色球送到紅色目的地，透過位於 ttyUSB0 控制 Arduino：
        $ python3 ./transporter.py --ball-color=BLUE --dest-color=RED --tty-device=/dev/ttyUSB0

    2. 在 Mac 上不接 Arduino 開發，以 console 查看送出的 action code：
        $ python3 ./transporter.py --debug --imshow --ball-color=BLUE --dest-color=RED

more:
    完整專案: https://github.com/choznerol/BallTransporterServer'''


def parse_args(args):
    """ 處理參數，翔見 $ python3 transporter.py --help """
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--ball-color', help='目標球的顏色，目前支援：{}'.format(list(colors.BALL_COLOR_HSV_RANGE.keys())),
                        dest='ball', required=True)
    parser.add_argument('--dest-color', help='目的地的顏色，目前支援：{}'.format(list(colors.DEST_COLOR_HSV_RANGE.keys())),
                        dest='dest', required=True)
    parser.add_argument('--tty-device', dest='tty', default='/dev/ttyUSB0',
                        help='''接收 action code 的 tty 裝置。預設為 RPi 的 /dev/ttyUSB0，在 Mac 可能是 /dev/tty.usbmodem1421，
                        可用 ls /dev/*tty* 確認。使用 --debug 時無作用''')
    parser.add_argument('--tty-baud', dest='baud', default=115200, type=int,
                        help='接收 action code 的 tty 裝置的 Baud Rate。預設為 115200')
    parser.add_argument('--zigzag-period', help='找不到目標時蛇行的週期，單位為楨數（VideoCapture 的 frame）',
                        dest='zigzag_period', type=int, default=10)
    parser.add_argument(
        '--imshow', help='以 cv2.imshow 秀出處理後的影像（debug用）', dest='imshow', action='store_true')
    parser.add_argument(
        '--debug', help='不使用 Serial 將 action code 送到 tty device ，而是直接印出 action code（debug用）', dest='debug', action='store_true')

    args = parser.parse_args()
    return args