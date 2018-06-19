import serial


ACTION_CODE_MAPPING = {
    0: '停',  # 不動
    1: '左',  # 左轉
    2: '右',  # 右轉
    3: '前',  # 前進
    4: '後',  # 後退
    5: '夾',  # 關爪子
    6: '放',  # 開爪子
}


class ArduinoController:
    """ 透過 Serial 控制 Arduino 的介面，傳送約定好的 0~6 的 Action code 控制作動 """
    def __init__(self, device, baud_rate=115200):
        """ 儲存所有送出的 action code。可用於決定週期性蛇行的方向（zigzag()），或校正車體方向面對正前方（尚未實作） """
        self._history = []
        self.debug = True if not device else False # 若未指定 device 則進入 debug 模式

        if not self.debug:
            try:
                self.ser = serial.Serial(device, baud_rate)
            except Exception as e:
                print('無法透過 tty 裝置 {0} 建立連線（baud rate={1}），請檢查與 Arduino 的連線！'.format(
                    device, baud_rate))
                raise e

    def dispatch(self, code):
        if code < 0 or code > 6:
            raise ValueError(
                'action code 須為 0 ~ 6 的整數！（0 不動, 1 左轉, 2 右轉, 3 前進 , 4 後退, 5 關爪子, 6 開爪）')
        if self.debug:
            self.print_action(code)
        else:
            encoded = str(code).encode('ASCII')
            self.ser.write(encoded)
        self._history.append(code)

    def print_action(self, code=None):
        """ 印出 Action code 代表的動作 """
        action = ACTION_CODE_MAPPING[code]
        print(action)

    def zigzag(self, period=10):
        """ 間歇性地左右蛇行，週期 period 的單位為禎數 """
        if len(self._history) % period <= (period / 2):
            self.dispatch(1)
        else:
            self.dispatch(2)

    def __str__(self):
        return 'ArduinoController(_history[{0}]{1})'.format(
            len(self._history), self._history)


# ArduinoController 測試
if __name__ == '__main__':
    ac = ArduinoController(None, 9600)
    ac.dispatch(3)
    ac.print_action()  # 印出 ^ （上）
    ac.dispatch(4)
    ac.print_action()  # 印出 V （下）
    ac.dispatch(1)
    ac.print_action()  # 印出 < （左）
    ac.dispatch(2)
    ac.print_action()  # 印出 > （右）
    ac.print_action(5)  # 印出 X （夾）

    # 蛇行
    count = 0
    while count < 50:
        ac.zigzag()
        ac.print_action() # 印出 <<>>>><<<<<<>>>><<<<<<>>>><<<<<<>>>><<<<<<>>>><<<< ...（左右交替）
        count += 1

