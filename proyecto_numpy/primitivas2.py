import cv2 as cv
import numpy as np 

img = np.ones((500,500,3), np.uint8)*255 
cv.rectangle(img, (10,10), (200,100), (255,0,0), 3) #-1 rellena el rectangulo completo    
# cv.circle(img, (255,255), 33, (23, 43, 144), -1 )
# cv.circle(img, (255,255), 15, (23, 43, 255), -1 )
# cv.line(img, (255,255), (300,100), (0,255,0), 4)

while True:
    cv.circle(img, (i, i), 20, (255, 0, 0), -1 )
    cv.imshow('img', img)
    img = np.ones((500,500,3), np.uint8)*255 
    cv.waitKey(10)

cv.imshow('img',img)
cv.waitKey(0)
cv.destroyAllWindows()
