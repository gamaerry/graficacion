import cv2 as cv
import numpy as np

img = cv.imread("res/frutas.png")

cv.lines(img, (x1, y1), (x2, y2), (r, g, b), valor)
cv.circle(img,(x1, y1), r, (r,g,b), valor)

# Operador puntual modifica la intensidad de un solo pixel
# Operador ventana modifica la intensidad de un grupo de pixeles
# transformacion geometrica rotaciones, traslaciones, etc

cv.imshow("img", img)
cv.waitKey(0)
cv.destroyAllWindows()
