#import "@local/gama:1.0.0":*
#show: body => documento(
  "Visión artificial",
  "Algoritmos Característicos de Visión Artificial y su Aplicación en Realidad Aumentada",
  autores: (
    (
      nombre: "Luis Gerardo López Hernández",
      idAlterno: "24121302",
      correo: "l24121302@morelia.tecnm.mx"
    ),
  ),
  "Mayo del 2026",
  body
)

La visión artificial es una rama de la informática y la inteligencia artificial cuyo objetivo es permitir que las máquinas interpreten y comprendan información visual proveniente de imágenes o video. Sus aplicaciones abarcan múltiples áreas como robótica, medicina, seguridad, vehículos autónomos y Realidad Aumentada (RA).

La Realidad Aumentada combina elementos virtuales con el entorno real en tiempo real. Para lograrlo, necesita algoritmos capaces de detectar objetos, reconocer patrones, estimar movimiento y comprender escenas visuales.

Paralelamente, el aprendizaje profundo (*Deep Learning*) ha revolucionado la visión artificial mediante redes neuronales capaces de aprender automáticamente características complejas a partir de grandes cantidades de datos.

= 1. Algoritmos Característicos de Visión Artificial

== 1.1 Detección de Bordes

La detección de bordes identifica cambios bruscos de intensidad en una imagen. Los bordes representan límites de objetos y son fundamentales para segmentación y reconocimiento.

=== Algoritmo Sobel

Utiliza convoluciones para calcular gradientes horizontales y verticales.

*Funcionamiento:*
- Se aplican filtros matriciales sobre la imagen.
- Se calcula la variación de intensidad.
- Los cambios altos indican bordes.

*Ventajas:*
- Simple y rápido.
- Bajo costo computacional.

*Desventajas:*
- Sensible al ruido.

=== Algoritmo Canny

Es uno de los detectores de bordes más utilizados.

*Proceso:*
1. Suavizado con filtro Gaussiano.
2. Cálculo de gradientes.
3. Supresión de no máximos.
4. Umbralización con histéresis.

*Ventajas:*
- Bordes más precisos.
- Reduce ruido.

*Aplicación en RA:*
- Identificación de superficies y contornos para colocar objetos virtuales.

== 1.2 Transformada de Hough

Permite detectar formas geométricas como líneas y círculos.

*Funcionamiento:*
Cada punto de una imagen vota en un espacio paramétrico. Los máximos representan formas detectadas.

*Aplicaciones:*
- Detección de carriles.
- Reconocimiento de patrones geométricos.

*Uso en RA:*
- Localización de marcadores y patrones visuales.

== 1.3 Detección de Características

Busca puntos distintivos en imágenes.

=== SIFT

Detecta puntos clave invariantes a:
- Escala
- Rotación
- Iluminación parcial

*Funcionamiento:*
1. Construcción de pirámides gaussianas.
2. Detección de extremos.
3. Asignación de orientación.
4. Generación de descriptores.

*Ventajas:*
- Muy robusto.

*Desventajas:*
- Alto costo computacional.

=== SURF

Versión optimizada de SIFT.

*Características:*
- Más rápido.
- Menor precisión relativa.

*Uso en RA:*
- Reconocimiento de imágenes objetivo.

=== ORB

Alternativa ligera y libre de patentes.

*Ventajas:*
- Muy rápido.
- Adecuado para dispositivos móviles.

*Aplicación:*
- Seguimiento en tiempo real.

== 1.4 Optical Flow

Estima movimiento entre cuadros consecutivos de video.

=== Lucas-Kanade

Calcula desplazamiento local de píxeles.

*Aplicaciones:*
- Seguimiento de objetos.
- Estimación de movimiento de cámara.

*Uso en RA:*
- Mantener alineados los objetos virtuales.

== 1.5 SLAM

SLAM significa _Simultaneous Localization and Mapping_.

*Objetivos:*
- Localizar la cámara.
- Construir un mapa del entorno simultáneamente.

*Funcionamiento general:*
1. Captura del entorno.
2. Detección de puntos clave.
3. Estimación de posición.
4. Actualización del mapa.

*Tipos:*
- Visual SLAM
- RGB-D SLAM
- LiDAR SLAM

*Aplicación en RA:*
- Posicionamiento estable de objetos virtuales.

#pagebreak()

= 2. Aplicación de la Visión Artificial en Realidad Aumentada

== 2.1 Seguimiento de Marcadores

Se utilizan imágenes o códigos especiales.

*Proceso:*
1. Detección del marcador.
2. Extracción de esquinas.
3. Estimación de pose 3D.
4. Renderizado del objeto virtual.

*Ejemplos:*
- QR
- ArUco

== 2.2 Markerless AR

No requiere marcadores físicos.

*Tecnologías utilizadas:*
- SLAM
- Detección de planos
- Redes neuronales

*Funcionamiento:*
- El sistema detecta superficies.
- Calcula profundidad y orientación.
- Inserta objetos virtuales coherentemente.

== 2.3 Reconocimiento de Objetos

La visión artificial permite reconocer:
- Rostros
- Objetos
- Gestos
- Texto

*Aplicaciones:*
- Filtros faciales
- Traducción visual
- Asistentes inteligentes

#pagebreak()

= 3. Aprendizaje Profundo

El aprendizaje profundo es una subrama del aprendizaje automático basada en redes neuronales multicapa.

Busca imitar parcialmente el funcionamiento del cerebro humano mediante neuronas artificiales conectadas.

== 3.1 Redes Neuronales

Una red neuronal está compuesta por:
- Capa de entrada
- Capas ocultas
- Capa de salida

Cada neurona:
1. Recibe entradas.
2. Multiplica por pesos.
3. Suma resultados.
4. Aplica una función de activación.

*Modelo matemático:*

$
y = f(sum_(i=1)^n w_i x_i + b)
$

Donde:
- $x_i$: entradas
- $w_i$: pesos
- $b$: sesgo
- $f$: función de activación

== 3.2 El Perceptrón

El perceptrón es la forma más básica de red neuronal.

*Funcionamiento:*
1. Recibe entradas.
2. Calcula suma ponderada.
3. Aplica función escalón.
4. Produce salida binaria.

*Modelo:*

$
y = cases(1 & "si " sum w_i x_i + b > 0, 0 & "en otro caso")
$

*Limitaciones:*
- Solo resuelve problemas linealmente separables.

== 3.3 Redes Neuronales Profundas

Las redes profundas contienen múltiples capas ocultas.

*Ventajas:*
- Aprenden patrones complejos.
- Extraen características automáticamente.

*Desventajas:*
- Requieren gran poder computacional.
- Necesitan grandes cantidades de datos.

#pagebreak()

= 4. Redes Convolucionales (CNN)

Las CNN son fundamentales en visión artificial.

Utilizan:
- Convoluciones
- Pooling
- Capas densas

== Funcionamiento

=== Convolución

Filtros recorren la imagen detectando:
- Bordes
- Texturas
- Formas

=== Pooling

Reduce dimensiones conservando información relevante.

=== Clasificación

Las capas finales clasifican objetos.

*Aplicaciones:*
- Reconocimiento facial
- Detección de objetos
- Segmentación semántica
- RA inteligente

*Arquitecturas conocidas:*
- AlexNet
- VGG
- ResNet
- YOLO

#pagebreak()

= 5. Aplicación del Deep Learning en Realidad Aumentada

== 5.1 Detección de Objetos

Modelos como YOLO identifican objetos en tiempo real.

*Aplicación:*
- Etiquetado inteligente de objetos físicos.

== 5.2 Seguimiento Facial

Las redes neuronales detectan:
- Ojos
- Boca
- Expresiones

*Aplicación:*
- Filtros faciales.

== 5.3 Segmentación Semántica

Clasifica cada píxel de una imagen.

*Permite:*
- Separar fondo y personas.
- Interacción avanzada con objetos virtuales.

== 5.4 Estimación de Profundidad

Las CNN pueden inferir profundidad usando cámaras monoculares.

*Uso:*
- Oclusión realista en RA.

= 6. Ventajas y Desafíos

== Ventajas

- Interacción natural.
- Automatización visual.
- Alta precisión.
- Experiencias inmersivas.

== Desafíos

- Alto costo computacional.
- Sensibilidad a iluminación.
- Requerimiento de grandes datasets.
- Latencia en tiempo real.

= Conclusión

La visión artificial constituye una tecnología esencial para el desarrollo de sistemas modernos de Realidad Aumentada. Algoritmos clásicos como Canny, SIFT y SLAM permiten detectar y comprender el entorno visual, mientras que el aprendizaje profundo y las redes neuronales han incrementado significativamente la precisión y capacidad de reconocimiento de objetos y escenas.

La combinación entre visión artificial y Deep Learning ha permitido crear aplicaciones avanzadas capaces de interactuar inteligentemente con el entorno físico en tiempo real.

= Referencias

- Richard Szeliski — _Computer Vision: Algorithms and Applications_
- Ian Goodfellow, Yoshua Bengio, Aaron Courville — _Deep Learning_
- Rafael C. Gonzalez, Richard E. Woods — _Digital Image Processing_
- David A. Forsyth, Jean Ponce — _Computer Vision: A Modern Approach_
- OpenCV Documentation
- ARCore Documentation
- ARKit Documentation
