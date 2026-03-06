import cv2 as cv 

rostro = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
cap = cv.VideoCapture(0)

while True:
    ret, img = cap.read()
    gris = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    rostros = rostro.detectMultiScale(gris, 1.3, 5)
    for(x,y,w,h) in rostros:
        centro_cara = (x + w // 2, y + h // 2)
        ejes_cara = (int(w * 0.5), int(h * 0.6))
        # Contorno de la cara (ovalo principal)
        img = cv.ellipse(img, centro_cara, ejes_cara, 0, 0, 360, (234, 23, 23), 3)

        ojo_izq = (x + int(w * 0.3), y + int(h * 0.4))
        ojo_der = (x + int(w * 0.7), y + int(h * 0.4))
        img = cv.circle(img, ojo_izq, 21, (0, 0, 0), 2)
        img = cv.circle(img, ojo_der, 21, (0, 0, 0), 2)
        img = cv.circle(img, ojo_izq, 20, (255, 255, 255), -1)
        img = cv.circle(img, ojo_der, 20, (255, 255, 255), -1)
        img = cv.circle(img, ojo_izq, 5, (0, 0, 255), -1)
        img = cv.circle(img, ojo_der, 5, (0, 0, 255), -1)

        # Boca con elipse inferior (sonrisa)
        centro_boca = (x + w // 2, y + int(h * 0.72))
        ejes_boca = (int(w * 0.22), int(h * 0.12))
        img = cv.ellipse(img, centro_boca, ejes_boca, 0, 0, 180, (255, 255, 255), 3)

        # Nariz
        nariz_centro = (x + w // 2, y + int(h * 0.58))
        img = cv.circle(img, nariz_centro, int(w * 0.06), (40, 120, 240), -1)
        img = cv.circle(img, nariz_centro, int(w * 0.06), (0, 0, 0), 2)

        # Orejas
        oreja_izq_centro = (x - int(w * 0.08), y + int(h * 0.52))
        oreja_der_centro = (x + w + int(w * 0.08), y + int(h * 0.52))
        oreja_ejes = (int(w * 0.08), int(h * 0.14))
        img = cv.ellipse(img, oreja_izq_centro, oreja_ejes, 0, 0, 360, (120, 180, 240), -1)
        img = cv.ellipse(img, oreja_der_centro, oreja_ejes, 0, 0, 360, (120, 180, 240), -1)
        img = cv.ellipse(img, oreja_izq_centro, oreja_ejes, 0, 0, 360, (0, 0, 0), 2)
        img = cv.ellipse(img, oreja_der_centro, oreja_ejes, 0, 0, 360, (0, 0, 0), 2)

        # Barba de Santa Claus
        barba_centro = (x + w // 2, y + int(h * 0.88))
        barba_ejes = (int(w * 0.36), int(h * 0.22))
        img = cv.ellipse(img, barba_centro, barba_ejes, 0, 0, 360, (255, 255, 255), -1)
        img = cv.ellipse(img, barba_centro, barba_ejes, 0, 0, 360, (220, 220, 220), 2)

        # Volumen lateral de la barba
        barba_izq = (x + int(w * 0.34), y + int(h * 0.84))
        barba_der = (x + int(w * 0.66), y + int(h * 0.84))
        barba_lado_ejes = (int(w * 0.14), int(h * 0.15))
        img = cv.ellipse(img, barba_izq, barba_lado_ejes, -20, 0, 360, (255, 255, 255), -1)
        img = cv.ellipse(img, barba_der, barba_lado_ejes, 20, 0, 360, (255, 255, 255), -1)
        img2=  img[y:y+h,x:x+w]
        cv.imshow('img2', img2)
    cv.imshow('img', img)
    if cv.waitKey(1)== ord('q'):
        break
    
cap.release()
cv.destroyAllWindows()
