import cv2 as cv
import numpy as np
img = cv.imread('res/etapas.png')

'''
x,y,z=img.shape
b,g,r=cv.split(img)

img2 = np.zeros((x,y), np.uint8)
mr=cv.merge([img2,img2,r])
mg=cv.merge([img2,g,img2])
mb=cv.merge([b,img2,img2])
nueva1=cv.merge([r,g,b])
nueva2=cv.merge([g,b,r])
nueva3=cv.merge([b,r,g])

cv.imshow('b',mb)
cv.imshow('g',mg)
cv.imshow('r',mr)
cv.imshow('nueva1', nueva1)
cv.imshow('nueva2', nueva2)
cv.imshow('nueva3', nueva3)
'''


cv.imshow('img',img)


cv.waitKey(0)
cv.destroyAllWindows()
