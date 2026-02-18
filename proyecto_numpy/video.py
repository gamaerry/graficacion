import cv2 as cv
import numpy as np

# captura = cv.VideoCapture("res/wim-hof.mkv")
captura = cv.VideoCapture(0)
conexion, img = captura.read()
x,y,z=img.shape
fondo=np.zeros((x,y), np.uint8)
cv.imshow('fondo',fondo)

while True:
    conexion, img = captura.read()
    if conexion:
        r,g,b=cv.split(img)
        mr=cv.merge([fondo,fondo,r])
        mg=cv.merge([fondo,g,fondo])
        mb=cv.merge([b,fondo,fondo])
        cv.imshow('mr',mr)
        cv.imshow('mg',mg)
        cv.imshow('mb',mb)
        cv.imshow('img',img)
    else:
        print("No se pudo obtener fuente de video")
        break
    k=cv.waitKey(1)
    if k==27:
        break

captura.release()
cv.destroyAllWindows()
