import cv2
import numpy as np

img = cv2.imread('m1_oscura.png', cv2.IMREAD_GRAYSCALE)
h, w = img.shape[:2]
nuevo_lienzo = np.zeros((h, w), dtype=np.uint8)

# --- MODO RAW ---
# Recorre con un for y multiplica por 50
for i in range(h):
    for j in range(w):
        nuevo_lienzo[i,j] = img[i, j] * 50
np.clip(nuevo_lienzo, 0, 255)
cv2.imshow("mensaje descubierto", nuevo_lienzo)
cv2.waitKey(0)
cv2.destroyAllWindows()

# --- MODO OPENCV ---
# Usa la magia de la vectorización


