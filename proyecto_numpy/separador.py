import cv2 as cv
import numpy as np

img = cv.imread("res/frutas.png")
hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

# Definir el rango inferior y superior para detectar verde
lower_green1 = np.array([35,60,60])  # Hue, Saturación, Brillo mínimos
upper_green1 = np.array([85, 255, 255])  # Hue, Saturación, Brillo máximos
# Crear una máscara que solo incluya los píxeles dentro del rango
# mask0 = cv.inRange(hsv, lower_green0, upper_green0)
mask1 = cv.inRange(hsv, lower_green1, upper_green1)
# Aplicar la máscara a la imagen original
mask = mask1 

result = cv.bitwise_and(img, img, mask=mask)
cv.imshow('img_hsv', hsv)
cv.imshow('img_original', img)
# cv.imshow("Color Detectado", result)
cv.imshow("Color mascara", mask)
cv.waitKey(0)
cv.destroyAllWindows()
