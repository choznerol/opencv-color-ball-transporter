import sys
import time
import select


def handle_input(user_input):
    """ 收到使用者輸入時的 callback function """
    print('\n發現 stdin 可讀取，收到使用者輸入：{} '.format(user_input))
    # sys.stdout.flush()


def routine_work():
    """ 持續執行的主要業務（e.g. 持續擷取 frame 做影像辨識） """
    print('持續跑影像辨識...')


count = 0
while count < 20:
    # If there's input ready, do handle_input(), else do routine_work()
    # Note timeout is zero so select won't block at all.
    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        user_input = sys.stdin.readline().strip()
        if user_input:
            handle_input(user_input)
    else:
        routine_work()
    time.sleep(0.3)
    count += 1
