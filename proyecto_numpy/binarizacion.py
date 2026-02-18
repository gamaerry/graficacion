import cv2 as cv
import numpy as np
img_gris = cv.imread('res/bird.jpg',1)
img_color = cv.cvtColor(img_gris, cv.COLOR_BGR2GRAY)
x,y=img_color.shape
img_resultado = np.zeros((x,y), np.uint8)

for i in range(x):
    for j in range(y):
        if(img_color[i,j]>128):
            img_resultado[i,j]=255
        else:
            img_resultado[i,j]=0;


cv.imshow('img_resultado',img_resultado)
cv.imshow('img_color',img_color)
cv.imshow('img_gris',img_gris)
cv.waitKey(0)
cv.destroyAllWindows()
