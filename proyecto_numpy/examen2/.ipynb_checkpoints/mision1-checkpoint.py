import cv2
import numpy as np

img = cv2.imread("m1_oscura 1.png", cv2.IMREAD_GRAYSCALE)

h, w = img.shape

# Fase 1: multiplicar por 50
raw_x50 = np.zeros((h, w), dtype=np.int32)
for y in range(h):
    for x in range(w):
        raw_x50[y, x] = img[y, x] * 50

raw_x50 = np.clip(raw_x50, 0, 255).astype(np.uint8)
cv2.imwrite("m1_recuperado_x50.png", raw_x50)

# Fase 2: sumar +20
raw_x50_mas20 = np.zeros((h, w), dtype=np.int32)
for y in range(h):
    for x in range(w):
        raw_x50_mas20[y, x] = int(raw_x50[y, x]) + 20

raw_x50_mas20 = np.clip(raw_x50_mas20, 0, 255).astype(np.uint8)
cv2.imwrite("m1_recuperado_x50_mas20.png", raw_x50_mas20)

print("RAW listo:", raw_x50.shape, raw_x50_mas20.shape)

# ── MODO VECTORIZADO ──────────────────────────────────────────────────────────

vec_x50     = np.clip(img.astype(np.int32) * 50,      0, 255).astype(np.uint8)
vec_x50_m20 = np.clip(img.astype(np.int32) * 50 + 20, 0, 255).astype(np.uint8)

# Verificación: deben ser idénticos al modo raw
print("Vectorizado == Raw (x50)    :", np.array_equal(vec_x50, raw_x50))
print("Vectorizado == Raw (x50+20) :", np.array_equal(vec_x50_m20, raw_x50_mas20))
