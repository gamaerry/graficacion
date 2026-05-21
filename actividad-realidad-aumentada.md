# Actividad A — Medición del marcador

- Mide el lado del cuadrado negro en cm.
- Pon MARKER_LENGTH_M en metros.
- Explica en 3 líneas qué pasa si pones el doble del valor real:

Se hace más pequeña la figura generada sobre el marcador detectado.

# Actividad B — Tetera vs esfera

- Captura pantalla con la tetera y otra con la esfera (tecla T).
- ¿Qué librería dibuja cada una? (GLUT vs GLU)

GLUT genera la tetera y GLU la esfera

# Actividad C — Ejes OpenCV (solo visión, opcional)

- Añade temporalmente en el bucle, antes de OpenGL, para ver ejes en una ventana OpenCV:

`if corners is not None:
    rvec, tvec = estimate_pose(corners, camera_matrix, dist_coeffs)
    dbg = frame.copy()
    cv2.drawFrameAxes(dbg, camera_matrix, dist_coeffs, rvec, tvec, MARKER_LENGTH_M * 0.5)
    cv2.imshow("debug ejes", dbg)
    cv2.waitKey(1)`
    
- Compara: los ejes RGB deben coincidir con la orientación del objeto OpenGL.

# Actividad D — Calibración (mejora la alineación)

- Si tienes tablero chessboard, calibra y guarda:
`
# Esqueleto: tras calibrateCamera, guardar:
np.savez("camera_ar.npz", camera_matrix=K, dist_coeffs=dist, image_size=(w,h))
`
- Coloca camera_ar.npz junto al .py. Sin archivo, el programa usa intrínsecos aproximados.

<img width="228" alt="1 3" src="https://github.com/user-attachments/assets/06651633-532b-4d27-9f7f-33f4ae0846e2" />

<img width="228" alt="1 1" src="https://github.com/user-attachments/assets/ed564d44-3690-4352-845a-a3a0e36866f9" />

<img width="228" alt="1 2" src="https://github.com/user-attachments/assets/0ba96521-45c4-421c-be8b-2f975aa45ff7" />


