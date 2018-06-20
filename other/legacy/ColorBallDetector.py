#!/usr/bin/env python3 -tt
# -*- coding: utf-8 -*-
"""
用法: python3 ./ColorBallDetector.py [--debug] [--color-hue ./COLOR_HUE.yml] COLOR

參數說明：
  COLOR         要偵測的顏色（可在 COLOR_RANGE_HSV 裡增加、調整）
  --debug       用 cv2.imshow() 顯示偵測到的指定顏色球型圖像
  --color-hue   (尚未實作）以檔案指定顏色偵測範圍的 hue 值上下限
"""

import sys
import os
import cv2
import math
import serial
import getopt
import numpy as np

# TODO: use ./BALL_COLOR_HUE.yml instead
# Color threshold in HSV (hue, saturation, value)
COLOR_RANGE_HSV = {
    "BLUE": [np.array([90, 50, 50]), np.array([120, 255, 255])],  # Blue's hue is 120
    "GREEN": [np.array([45, 50, 50]), np.array([70, 255, 255])],  # Green's hue is 60
    "RED": [np.array([0, 50, 50]), np.array([10, 255, 255])],  # Red's hue is 0
    "RED": [np.array([170, 50, 50]), np.array([180, 255, 255])]  # Red's hue is 0
}

"""
接收圖片與目標顏色範圍，回傳裁切掉其他顏色後的圖片
"""
def crop_by_color_range(img, from_hsv, to_hsv):
    img = cv2.medianBlur(img, 11)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, np.array(from_hsv), np.array(to_hsv))

    # Bitwise-AND mask and original image
    cropped = cv2.bitwise_and(hsv, hsv, mask=mask)
    intensity = cropped.sum()
    return cropped, intensity


"""
接收圖片，以 HoughTransform() 尋找圓形，並回傳裁剪後的圖片與圓座標
"""
def crop_circle(img):
    length, width, _ = img.shape
    # 以模糊忽略細節
    img = cv2.medianBlur(img, 11)
    # 用灰階圖找圓(比起用
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,
        # dp – Inverse ratio of the accumulator resolution to the image resolution. For example, if dp=1 , the
        # accumulator has the same resolution as the input image. If dp=2 , the accumulator has half as big width
        # and height.
        5,
        # minDist – Minimum distance between the centers of the detected circles. If the parameter is too small,
        # multiple neighbor circles may be falsely detected in addition to a true one. If it is too large, some
        # circles may be missed.
        math.floor(width / 2),
        # Higher threshold of the two passed to the Canny() edge detector (the lower one is twice smaller).
        param1=80,
        # Accumulator threshold for the circle centers at the detection stage. The smaller it is, the more false
        # circles may be detected. Circles, corresponding to the larger accumulator values, will be returned first.
        param2=250,
        minRadius=math.floor(width / 10),
        maxRadius=math.ceil(0.9 * width / 2)
    )

    cropped = mark_circle(img, circles) # TODO: Crop instead of mark
    return cropped, circles


"""
接收 image 與圓型座標，回傳標註後的 image
"""
def mark_circle(image, circles):
    num_circles = 0
    if circles is not None:
        circles_found = np.uint16(np.around(circles))
        num_circles = circles_found.shape[1]

    # 標記找到的圓
    if num_circles is not 0:
        for i in circles_found[0, 0:]:
            cv2.circle(image, (i[0], i[1]), i[2], (0, 255, 0), 5)
            cv2.circle(image, (i[0], i[1]), 2, (0, 0, 255), 8)
    return image


"""
測試主程式：以 get_color_circle() 偵測圓的座標，用 mark_circle() 在圖片標上圓圈，最後用 imshow() 顯示在螢幕上
"""
def main():
    optlist, args = getopt.getopt(sys.argv[1:], 'x', ['debug', 'tty-device=', ''])

    options = {}
    options.setdefault('debug', False)
    options.setdefault('tty-device', '/dev/ttyUSB0')
    # options.setdefault('tty-device', '/dev/tty.usbmodem1421') # Mac

    while len(optlist) > 0:
        (key, val) = optlist.pop()
        if key == '--debug':
            options.update({'debug': True})
        elif key == '--tty-device':
            options.update({'tty-device': val})
        else:
            print('未知的參數{}{}'.format(key, val))
            exit(1)

    print('[DEBUG] Running with', options)

    # ser = serial.Serial(options.get('tty-device'), 115200)

    color = args[-1]
    if color not in COLOR_RANGE_HSV:
        print('字典中找不到球色 `{}` 的 hue 值：'.format(color), COLOR_RANGE_HSV)
        sys.exit(1)

    hue_range = COLOR_RANGE_HSV[color]


    # Detect ball
    cp0 = cv2.VideoCapture(0)
    while True:
        ret0, frame0 = cp0.read()
        cropped_by_color, intensity = crop_by_color_range(frame0, hue_range[0], hue_range[1])
        circled, circles = crop_circle(cropped_by_color)

        # Debug 模式下顯示圖片、印出顯示方位
        if options.get('debug'):
            cv2.imshow('circled', circled)
            # 按下 q 關閉所有視窗
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                cp0.release()
                break

            # 顯示球的方位
            if circles is not None:
                circle_x = circles[0][0][0]
                width = circled.shape[1]
                hor_offset = (circle_x - (width / 2)) / (width / 2)
                print(hor_offset)
            else:
                print(None)

        # 以 Serial 傳送控制左右輪、夾爪的指令代碼
        # 格式：
        #   0 不動, 1 左轉, 2 右轉, 3 前進 , 4 後退, 5 關爪子, 6 開爪
        # msg = '3' # 預設前進
        # if circles is not None:
        #     circle_x = circles[0][0][0]
        #     width = circled.shape[1]
        #     hor_offset = (circle_x - (width / 2)) / (width / 2)
        #     if hor_offset > 0:
        #         msg = '1' # 右轉
        #     else:
        #         msg = '2' # 左轉
        # print('serial.write({})'.format(msg))
        # ser.write(msg.encode('ASCII'))
        # if ser.inWaiting():
        #     print(ser.read().decode('ASCII'))
        # else:
        #     print('NA')

"""
執行 main() 開發測試
"""
if __name__ == '__main__':
    main()
