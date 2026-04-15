# Operación Espejismo II (Graficación Táctica Examen)

## Introducción a la Misión

Agentes, hemos interceptado un paquete de evidencias visuales. El enemigo está usando **graficación 2D** para fragmentar claves, camuflar mensajes y alterar geometría.

**Reglas:**
- Si trabajas en escala de grises, mantén el rango en 0..255.
- Siempre que multipliques o sumes intensidades, usa saturación: `np.clip(..., 0, 255)`.
- Entrega imágenes (PNG) y tu reporte final en Markdown.

**Archivos base (en esta misma carpeta):**
- `m1_oscura.png`
- `m2_mitad1.png`
- `m2_mitad2.png`
- `m4_ruido.png`

---

## Misión 1: El Mensaje Subexpuesto II (Operadores Puntuales en 2 fases)

### La Historia

Interceptamos una imagen (`m1_oscura.png`) casi negra. Pero ahora el enemigo aplicó dos etapas:

1. División (para "apagar" el texto).
2. Resta de un sesgo pequeño (para que, al recuperar, se "queme" si no saturas).

### Las Pistas

- Recuperación sugerida:
  - Paso A: multiplicar por 50
  - Paso B: sumar una constante (ej. 15 o 25)
  - Saturar a 0..255

### Tu Tarea

1. **Modo Raw:** usa ciclos anidados para recuperar: multiplicar por 50 y luego sumar +20 (con saturación).
2. **Modo NumPy/OpenCV:** haz lo mismo pero vectorizado (`img*50 + 20` o `cv2.multiply` + `cv2.add`).
3. Guarda dos evidencias:
   - `m1_recuperado_x50.png`
   - `m1_recuperado_x50_mas20.png`

```python
import cv2
import numpy as np

img = cv2.imread("m1_oscura.png", cv2.IMREAD_GRAYSCALE)

# TODO MODO RAW:
# - Crear una matriz int32 para evitar overflow
# - Recorrer con ciclos anidados (y,x)
# - Multiplicar cada píxel por 50
# - Aplicar np.clip a 0..255 y guardar como uint8 -> m1_recuperado_x50.png
#
# TODO SEGUNDA FASE (RAW):
# - Sumar +20 a cada píxel recuperado
# - Aplicar np.clip 0..255 y guardar -> m1_recuperado_x50_mas20.png
#
# TODO MODO VECTORIZADO (opcional):
# - Hacer lo mismo sin for (con operaciones NumPy o cv2.multiply/cv2.add)
```

---

## Misión 2: El QR Fragmentado II (Traslación + Rotación + Ensamble)

### La Historia

El QR sigue partido:
- La mitad superior (`m2_mitad1.png`) fue desplazada.
- La mitad inferior (`m2_mitad2.png`) fue rotada 180°.

Pero ahora debes **ensamblarlo con precisión**, dejando el código centrado en el lienzo final.

### Las Pistas

- Crea un lienzo blanco de 400x400.
- Corrige:
  - Mitad 1: traslación inversa hacia el origen.
  - Mitad 2: rotación inversa 180° sobre su centro y colocación en la parte inferior.

### Tu Tarea

1. Crea lienzo blanco 400x400 (3 canales).
2. Endereza ambas piezas con `cv2.warpAffine`.
3. Pega las piezas (sin solaparlas) para reconstruir el QR.
4. Guarda: `m2_qr_reconstruido.png`

```python
import cv2
import numpy as np

mitad1 = cv2.imread("m2_mitad1.png")
mitad2 = cv2.imread("m2_mitad2.png")

lienzo = np.full((400, 400, 3), 255, dtype=np.uint8)

# TODO:
# - Crear la matriz de traslación INVERSA para la mitad 1
#   (elige dx, dy correctos según dónde quedó la pieza)
# - Aplicar cv2.warpAffine a mitad1 para enderezarla
# - Pegar mitad1 enderezada en la parte superior del lienzo
#
# - Crear la matriz de rotación para des-rotar mitad 2 (180°) sobre su centro
# - Aplicar cv2.warpAffine a mitad2 para enderezarla
# - Pegar mitad2 enderezada en la parte inferior del lienzo
#
# - Guardar resultado final como m2_qr_reconstruido.png
```

---

## Misión 3: El Sello Biométrico II (Primitivas + Simetría)

### La Historia

El servidor principal requiere un sello geométrico, pero ahora incluye **patrones simétricos** y una marca de autenticidad.

### Instrucciones del Sello

- Lienzo: 600x600 color base `BGR(40, 20, 20)`.
- Círculo central amarillo en (300, 300) radio 170 grosor 3.
- Círculo interior amarillo en (300, 300) radio 110 grosor 2.
- Rectángulo rojo sólido (relleno) de (250, 260) a (350, 340).
- Dos líneas blancas diagonales de esquina a esquina (una `X`) grosor 2.
- **Marca simétrica**: coloca 8 círculos verdes pequeños (radio 8, rellenos) alrededor del centro, a 140 px de distancia (tipo brújula).
- Texto blanco: `SECTOR-9` centrado abajo (aprox y=560).

### Tu Tarea

1. Dibuja el sello EXACTAMENTE en ese orden.
2. Guarda: `m3_sello_forjado_v2.png`

```python
import cv2
import numpy as np
import math

img = np.zeros((600, 600, 3), dtype=np.uint8)
img[:] = (40, 20, 20)

# TODO (en el orden exacto):
# - Dibujar círculo exterior amarillo
# - Dibujar círculo interior amarillo
# - Dibujar rectángulo rojo relleno
# - Dibujar las 2 diagonales blancas (X)
# - Colocar 8 círculos verdes alrededor del centro a distancia 140 (usa sin/cos o simetrías)
# - Escribir el texto "SECTOR-9" en la parte baja
# - Guardar como m3_sello_forjado_v2.png
```

---

## Misión 4: La Frecuencia Térmica II (HSV + máscara + "limpieza" por convolución)

### La Historia

El enemigo ocultó la contraseña en (`m4_ruido.png`), pero ahora hay **ruido extra** que genera falsos positivos en la máscara.

### Las Pistas

- Segmentar Cyan en HSV (Hue ~ 90).
- Antes de segmentar, puedes suavizar con un kernel de promedio para reducir ruido:
  - Kernel promedio 3x3:
    ```
    [[1,1,1],
     [1,1,1],
     [1,1,1]] / 9
    ```

### Tu Tarea

1. Aplica un filtro por convolución (promedio 3x3) a la imagen BGR.
2. Convierte a HSV.
3. Segmenta con `cv2.inRange` usando un rango Cyan.
4. Guarda:
   - `m4_mask_cyan.png`
   - (opcional) `m4_suavizada.png`

```python
import cv2
import numpy as np

img = cv2.imread("m4_ruido.png")

# TODO:
# - Definir kernel promedio 3x3 (float32) y aplicar cv2.filter2D
# - (Opcional) guardar la imagen suavizada como m4_suavizada.png
# - Convertir a HSV con cv2.cvtColor
# - Definir límites low/high para Cyan
# - Crear máscara con cv2.inRange
# - Guardar máscara como m4_mask_cyan.png
```

---

## Misión 5: La Huella de Canales (Separación BGR + combinación)

### La Historia

Interceptamos (`m5_tricolor.png`) (debes generarla tú) donde la clave no está en HSV, sino en una **diferencia entre canales**.

### Las Pistas

- Si un mensaje está "escondido" en un canal, al separarlo con `cv2.split` puede verse.
- También puede revelarse con combinaciones tipo:
  - `abs(G - B)`
  - `R - G` (con saturación)

### Tu Tarea

1. Genera una imagen de 300x700 con fondo aleatorio (ruido) en BGR.
2. Escribe un texto con tinta "tramposa" que dependa de un solo canal (por ejemplo, pon texto en el canal G muy alto y en B bajo).
3. Guarda la evidencia: `m5_tricolor.png`
4. Recupera el mensaje probando:
   - Canal B
   - Canal G
   - Canal R
   - `abs(G - B)`
5. Guarda la mejor recuperación como: `m5_mensaje.png`

```python
import cv2
import numpy as np

# TODO GENERACIÓN (m5_tricolor.png):
# - Crear imagen 300x700 con ruido aleatorio en BGR
# - Escribir el mensaje con una "tinta tramposa" (elige un color que dependa fuerte de 1 canal)
# - Guardar como m5_tricolor.png
#
# TODO RECUPERACIÓN:
# - Separar canales: b, g, r = cv2.split(img)
# - Probar: canal b, canal g, canal r
# - Probar combinaciones: cv2.absdiff(g, b) y/o (r - g) con saturación
# - (Opcional) normalizar con cv2.normalize
# - Umbralizar (fijo u Otsu) para que el texto sea legible
# - Guardar la mejor como m5_mensaje.png
```

---

## Entregable: Reporte de Misión (Formato Markdown Examen)

### Instrucciones

Entrega un archivo `reporte_mision_v2.md` que incluya:
- Capturas/imágenes resultantes de cada misión
- Bloques de código que usaste (puede ser el final "limpio")
- Conclusiones

### Plantilla Base

```markdown
# Reporte de Misión: Graficación Táctica II
**Agente Especial:** [Tu Nombre/Matrícula]

---
## Evidencias
### Misión 1
- Imagen recuperada x50: (inserta)
- Imagen recuperada x50 + 20: (inserta)
- Código:

### Misión 2
- QR reconstruido: (inserta)
- Código:

### Misión 3
- Sello forjado: (inserta)
- Código:

### Misión 4
- Máscara Cyan: (inserta)
- Código:

### Misión 5
- Evidencia tricolor: (inserta)
- Mensaje recuperado: (inserta)
- Código:

---
## Análisis del Analista (Reflexiones Finales)

1. **Operadores puntuales (M1):** ¿Qué diferencia visual hay entre recuperar con multiplicación (x50) y recuperar con suma (+50)? ¿Cuál preserva mejor el contraste del texto?
> [Respuesta]

2. **Transformaciones geométricas (M2):** ¿Por qué es importante escoger el centro correcto al rotar una imagen con `getRotationMatrix2D`?
> [Respuesta]

3. **Convolución (M4):** ¿Por qué un filtro promedio puede ayudar a reducir falsos positivos antes de segmentar por HSV, y qué desventaja tiene sobre los bordes del texto?
> [Respuesta]

4. **Canales (M5):** ¿Por qué separar canales puede revelar información que en la imagen a color "no se ve" a simple vista?
> [Respuesta]
```
