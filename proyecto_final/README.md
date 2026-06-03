# Proyecto Final: Demo Procedural con OpenCV

**Materia:** Graficacion  
**Periodo:** Enero-Junio 2026  
**Nombre:** Luis Gerardo Lopez Hernandez  
**Grupo:** B

## Objetivo

Construir una demo procedural con Python 3, NumPy y OpenCV que muestre temas de graficacion por computadora: timeline, curvas parametricas, primitivas de dibujo, transformaciones geometricas, composicion por capas y postproceso. Todo se genera en tiempo real, sin imagenes externas, texturas descargadas ni modelos importados.

## Como ejecutar

Para la presentacion se recomienda usar el entorno de la materia:

```bash
source ~/Envs/proyecto_numpy/bin/activate
pip install -r requirements.txt
python demo.py --preview
```

El archivo `requirements.txt` se mantiene minimo para instalar solo lo necesario en caso de que otro equipo no tenga las dependencias.

## Como exportar video y capturas

```bash
python demo.py --export --captures
```

El comando genera:

- `renders/demo_procedural.mp4`
- `renders/scene_00_intro_-_superelipse.png`
- `renders/scene_01_lissajous.png`
- `renders/scene_02_rosa_polar.png`
- `renders/scene_03_hipotrocoide_mas_transformaciones.png`
- `renders/scene_04_lemniscata_mas_particulas.png`
- `renders/scene_05_espiral_final.png`
- `renders/mask_vignette.png`
- `renders/mask_radial_bloom.png`

## Timeline de escenas

La demo dura 48 segundos, a 800x600 y 30 FPS. Cada escena ocupa 8 segundos y la transicion ocurre al final de cada bloque usando `cv2.addWeighted`.

| Tiempo | Escena | Proposito visual |
| --- | --- | --- |
| 0-8s | Intro / Superelipse | Presentacion, texto procedural y orbitas con `ellipse` |
| 8-16s | Lissajous | Curva protagonista animada con puntos de pulso |
| 16-24s | Rosa polar | Composicion por mascara circular |
| 24-32s | Hipotrocoide | Figura transformada con rotacion, escala y shear |
| 32-40s | Lemniscata + particulas | Campo de puntos procedural con blur |
| 40-48s | Espiral final | Composicion final con espiral y curva mariposa |

## Ecuaciones parametricas

1. Superelipse: `x=sign(cos t)|cos t|^(2/n)`, `y=sign(sin t)|sin t|^(2/n)`.
2. Lissajous: `x=sin(a t + delta)`, `y=sin(b t)`.
3. Rosa polar: `r=cos(5 theta)`, `x=r cos(theta)`, `y=r sin(theta)`.
4. Hipotrocoide: `x=(R-r)cos(t)+d cos(((R-r)/r)t)`, `y=(R-r)sin(t)-d sin(((R-r)/r)t)`.
5. Lemniscata: `x=cos(t)/(1+sin^2(t))`, `y=sin(t)cos(t)/(1+sin^2(t))`.
6. Espiral logaritmica: `x=e^(0.075t)cos(t)`, `y=e^(0.075t)sin(t)`.

Todas las curvas se convierten a puntos de pantalla y se dibujan con `cv2.polylines`.

## Transformaciones implementadas

| Transformacion | Donde aparece | Implementacion |
| --- | --- | --- |
| Rotacion | Escena 3 | `cv2.getRotationMatrix2D` genera una matriz afin 2x3 |
| Escala | Escena 3 | El factor de escala se incluye en la matriz de rotacion |
| Shear | Escena 3 | Matriz `[[1, shear, 0], [0, 1, 0]]` aplicada con `cv2.warpAffine` |
| Composicion por capas | Escenas 2, 3 y 5 | `cv2.addWeighted`, mascara circular y mezcla por regiones |

## Primitivas usadas

La demo usa `cv2.line`, `cv2.circle`, `cv2.ellipse`, `cv2.fillPoly`, `cv2.polylines` y `cv2.putText`. Las escenas evitan recursos externos: cada forma, patron, fondo, mascara y particula se calcula con NumPy.

## Postproceso y mascaras generadas

El postproceso global incluye:

- Vignette: oscurece bordes para concentrar la atencion en el centro.
- Radial bloom: mezcla un blur radial suave para resaltar curvas luminosas.
- Scanlines: patron ligero de lineas horizontales.
- Posterize: cuantizacion de color para estilo de demo grafica.

Las mascaras exportadas son:

- `renders/mask_vignette.png`
- `renders/mask_radial_bloom.png`

## Tabla comparativa de resultados

| Requisito | Resultado |
| --- | --- |
| Resolucion 800x600 | Cumplido |
| 30 FPS objetivo | Cumplido en exportacion con `VideoWriter` a 30 FPS |
| Duracion 30-60s | Cumplido, 48 segundos |
| Python 3 | Cumplido |
| Solo `numpy` y `opencv-python` | Cumplido |
| Sin imagenes externas | Cumplido |
| Minimo 6 escenas | Cumplido |
| Minimo 6 curvas parametricas | Cumplido |
| Minimo 2 transformaciones | Cumplido: rotacion, escala, shear y composicion |
| Primitivas visibles | Cumplido |
| Minimo 1 filtro/post | Cumplido: vignette, bloom, scanlines y posterize |
| Export final | Cumplido: MP4 y capturas |

## Respuestas de analisis

1. **Por que una timeline y no interaccion por clicks?**  
   Porque el objetivo es una demo procedural: el avance temporal controla escenas, animacion, transiciones y transformaciones sin depender del usuario.

2. **Por que usar curvas parametricas?**  
   Permiten generar geometria compleja a partir de ecuaciones. En OpenCV se convierten a arreglos de puntos y se dibujan eficientemente con `cv2.polylines`.

3. **Que aportan las matrices afines?**  
   Permiten aplicar rotacion, escala, traslacion y shear sobre una capa o figura. En la escena 3 se nota porque la nave cambia de orientacion, tamano e inclinacion con el tiempo.

4. **Por que aplicar postproceso?**  
   Unifica visualmente las escenas y demuestra procesamiento de imagen: mascaras, blur, mezcla de capas, scanlines y cuantizacion.

## Conclusion

La demo cumple la mision del curso al construir una escena audiovisual completa con matematicas, primitivas y procesamiento de imagen. OpenCV se usa tanto para dibujar como para transformar, componer y exportar el resultado final.
