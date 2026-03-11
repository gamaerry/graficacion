import cv2
import numpy as np

img = cv2.imread("vehiculo.jpg")
h, w = img.shape[:2]
tx = 600
ty = 400
M = np.float32([
    [1, 0, tx],
    [0, 1, ty],
])
desplazadaOpen = cv2.warpAffine(img, M, (w + tx, h + ty))

desplazadaRaw = np.zeros((h + ty, w + tx, 3), dtype=np.uint8)
for i in range(h):
    for j in range(w):
        desplazadaRaw[i + ty, j + tx] = img[i, j]

cv2.imshow("Original", img)
cv2.imshow("DesplazadaOpen", desplazadaOpen)
cv2.imshow("DesplazadaRaw", desplazadaRaw)
cv2.waitKey(0)
cv2.destroyAllWindows()
