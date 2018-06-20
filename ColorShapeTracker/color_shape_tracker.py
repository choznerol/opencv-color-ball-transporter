import cv2
import numpy as np
import math

CIRCLE = 'CIRCLE'

CONTOUR = 'CONTOUR'

ACCEPT_SHAPE = [CIRCLE, CONTOUR]

# 將「位於畫面中間」定義為水平方向 40~60% 之間
CENTER_RANGE = [0.4, 0.6]

""" 畫面中視為在爪子範圍內的矩形（[x位置, y位置, 寬, 高]，單位為佔畫面長寬百分比） """
DEFAULT_CATCH_ZONE = [ .5, .7, .1, .1 ]

"""
可辨識特定顏色（以 hue 值範圍表示）、形狀（圓形及多邊形）。負責創建 VideoCapture 實體及 OpenCV 的相關運算
"""
class ColorShapeTracker:
    def __init__(self, device, from_hue, to_hue, shape, catch_zone=DEFAULT_CATCH_ZONE, debug=False):
        if shape in ACCEPT_SHAPE:
            self.shape = shape
        else:
            raise ValueError('目前支援的形狀只有：', ACCEPT_SHAPE)
        cap = cv2.VideoCapture(device)
        if not cap.isOpened():
            cap.open(device)
        self.cap = cap
        self.frame = None
        self.target_hue = [from_hue, to_hue]

        self._update_frame()
        self.height, self.width, _ = self.frame.shape
        self.catch_zone_percentage = catch_zone
        self.catch_zone = [
            math.floor(catch_zone[0] * self.width),
            math.floor(catch_zone[1] * self.height),
            math.floor(catch_zone[2] * self.width),
            math.floor(catch_zone[3] * self.height),
        ]
        self.is_catchable = False

    """ 回傳找到的目標 shape，格式為：x, y, r, area，分別為目標的 x y 座標、半徑（若shape=CIRCLE）、面積大小。其中 x, y, r 的單位為所佔比例（介於 0 ~ 1.0）"""
    def find_one(self):
        self._update_frame()

        if self.shape == CIRCLE:
            cropped, area = self._crop_by_hue_range()
            self.frame = cropped
            circle = self._find_biggest_circle(cropped)
            self.imshow('x, y', circle)
            if circle is not None:
                self._update_catchable(circle)
                x_percentage = circle[0] / self.width
                y_percentage = circle[1] / self.height
                r_percentage = circle[2] / self.height
                return [x_percentage, y_percentage, r_percentage]
        # 未提供 shape，回傳：型心座標、面積

        elif self.shape == CONTOUR:
            return None, None, None, None

    """  """
    def is_target_catchable(self):
        return self.is_catchable

    """ 決定 target 座標是否落在 catch zone 之內 """
    def _update_catchable(self, target):
        x, y, w, h = self.catch_zone
        within_w = abs(x - target[0]) < w / 2
        within_h = abs(y - target[1]) < h / 2
        self.is_catchable = within_w and within_h

    """ 更新 frame """
    def _update_frame(self):
        _, self.frame = self.cap.read()

    def _crop_by_shape(self):
        if self.shape == CIRCLE:  # 目前僅支援圓形
            self._crop_by_circle()

    """ 根據 tracker 初始化時的 hue range 裁掉目標顏色以外的部分，並回傳裁切後的圖片，以及其面積 """
    def _crop_by_hue_range(self):
        img = cv2.medianBlur(self.frame, 11)
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(img, self.target_hue[0], self.target_hue[1])

        # Bitwise-AND mask and original image
        cropped = cv2.bitwise_and(img, img, mask=mask)
        area = cropped.sum()
        return cropped, area

    """ 以 HoughTransform() 找最大的一個圓形，回傳 (x, y, z）單位為畫面中的比例，介於0 ~ 1.0 """
    def _find_biggest_circle(self, img):
        img = cv2.medianBlur(img, 11)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,
           # dp – Inverse ratio of the accumulator resolution to the image resolution. For example, if dp=1 , the
           # accumulator has the same resolution as the input image. If dp=2 , the accumulator has half as big width
           # and height.
           5,
           # minDist – Minimum distance between the centers of the detected circles. If the parameter is too small,
           # multiple neighbor circles may be falsely detected in addition to a true one. If it is too large, some
           # circles may be missed.
           math.floor(self.width / 2),
           # Higher threshold of the two passed to the Canny() edge detector (the lower one is twice smaller).
           param1=80,
           # Accumulator threshold for the circle centers at the detection stage. The smaller it is, the more false
           # circles may be detected. Circles, corresponding to the larger accumulator values, will be returned first.
           param2=250,
           minRadius=math.floor(self.width / 10),
           maxRadius=math.ceil(0.9 * self.width / 2)
        )
        if circles is not None:
            return circles[0][0]

    """ 封裝 cv2.imshow，並加上 catch zone，以及找到的 circle 或 contour """
    def imshow(self, title='Untitled', target=None):
        # 標注夾球區域
        img = self._mark_catch_zone(self.frame, target)
        if target is not None:
            # 標注找到的 circle 或 contour
            img = self._mark_target(img, target)
        cv2.imshow(title, img)
        # 隨時可按下 q 關閉視窗
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            self.cap.release()
            exit(0)

    """ 在圖上畫出 catch zone 矩形 """
    def _mark_catch_zone(self, img, target):
        color = (0, 0, 255)  # 紅色框
        if self.is_catchable:
            color = (0, 255, 0)  # 綠色框
        x, y, w, h = self.catch_zone
        pt1, pt2 = (int(x-w/2), int(y-w/2)), (int(x+w/2), int(y+w/2))
        return cv2.rectangle(img, pt1, pt2, (0, 255, 0), 3)

    """ 在圖上畫出 target 座標 """
    @staticmethod
    def _mark_target(img, target):
        is_circle = len(target) == 3  # target 可能為圓形 (x, y, r) 或一般座標 (x, y)
        if is_circle:
            x, y, r = target
            return cv2.circle(img, (x, y), r, (0, 255, 0))
        else:
            x, y = target
            return cv2.circle(img, (x, y), 1, (0, 0, 255), 10)
