import cv2
import numpy as np
from pathlib import Path

MARKER_ID = 1
OUT = Path(f"marcador_aruco_id{MARKER_ID}.png")
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
if hasattr(cv2.aruco, "generateImageMarker"):
    img = cv2.aruco.generateImageMarker(dictionary, MARKER_ID, 400)
else:
    img = cv2.aruco.drawMarker(dictionary, MARKER_ID, 400)
border = 40
canvas = np.full((480, 480), 255, np.uint8)
canvas[40:440, 40:440] = img
cv2.imwrite(str(OUT), canvas)
print("OK ->", OUT)
