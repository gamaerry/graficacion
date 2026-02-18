import cv2 as cv
import numpy as np
import random
import math
import sys

n=600

def en_rango(i, j):
    return 0 < i < n-1 and 0 < j < n-1

img_tmp=np.ones([n,n], np.uint8)*255
img=img_tmp.copy()

for i in range (0,n):
    for j in range(0,n):
        params = [
            math.tan(j*i)**int(sys.argv[1]),
            ]
        x1 = (params[0]*256)
        if x1 > 0 and x1 < 256:
            img_tmp[i,j] = x1
            img[i,j] = x1
            if img_tmp[i,j] >= 1 or (en_rango(i,j) and (img_tmp[i+1,j]>=1 and img_tmp[i,j+1]>=1 and img_tmp[i-1,j]>=1 and img_tmp[i,j-1]>=1)):
                img[i,j] = 255        

cv.imshow('img',img)
cv.waitKey(0)
cv.destroyAllWindows()
