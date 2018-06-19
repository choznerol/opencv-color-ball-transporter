import numpy as np

BALL_COLOR_HSV_RANGE = {
    # Blue's hue is 120
    "BLUE": [np.array([90, 50, 50]), np.array([120, 255, 255])],
    # Green's hue is 60
    "GREEN": [np.array([45, 50, 50]), np.array([70, 255, 255])],
    "RED": [np.array([0, 50, 50]), np.array([10, 255, 255])],  # FIXME: 會被覆蓋
    # Red's hue is 0
    "RED": [np.array([170, 50, 50]), np.array([180, 255, 255])]
}

DEST_COLOR_HSV_RANGE = {
    # Blue's hue is 120
    "BLUE": [np.array([90, 50, 50]), np.array([120, 255, 255])],
    # Green's hue is 60
    "GREEN": [np.array([45, 50, 50]), np.array([70, 255, 255])],
    "RED": [np.array([0, 50, 50]), np.array([10, 255, 255])],  # FIXME: 會被覆蓋
    # Red's hue is 0
    "RED": [np.array([170, 50, 50]), np.array([180, 255, 255])]
}
