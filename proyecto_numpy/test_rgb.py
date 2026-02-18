import cv2 as cv
import numpy as np
import random
import math

img=np.ones([400,400], np.uint8)*255
img[1,1]=0
for i in range (400):
    for j in range(400):
        parametro = math.sin(math.radians((j%400)*(i%400)))
        x1 = parametro*255
        # print((j%16)*(i%16))
        if x1 > 0 and x1 < 256:
            img[i,j] = x1

cv.imshow('img',img)
cv.waitKey(0)
cv.destroyAllWindows()
