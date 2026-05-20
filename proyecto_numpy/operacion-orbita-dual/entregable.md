# Reporte de Misión: Órbita Dual (Cámara vs Objeto)
**Agente Especial:** Luis Gerardo López Hernández

## Objetivo
Este entregable documenta la diferencia entre transformar el objeto y transformar la cámara en OpenGL de pipeline fijo. También compara el uso de `glTranslatef` + `glRotatef` contra `gluLookAt`, y analiza el efecto de la iluminación cuando cambia el sistema de referencia en el que se define la luz.

## Archivos del trabajo
- Programa refactorizado: `misiones.py`
- Capturas esperadas:
  - `m1_objeto_rota.png`
  - `m1_camara_orbita.png`
  - `m2_lookat_orbita.png`
  - `m3_luz_objeto.png` (opcional)
  - `m3_luz_camara.png` (opcional)

## Misión 0: Diferencia entre mover objeto y mover cámara
### Idea central
Hay dos maneras de producir una animación parecida desde pantalla:

1. Rotar el objeto mientras la cámara permanece fija.
2. Mantener el objeto fijo y mover la cámara alrededor de él.

### Caso A: mover el objeto
La cámara queda ubicada en `(0, 0, -5)` y el objeto rota sobre su eje Y. En este caso la transformación visible pertenece al modelo, no a la vista.

### Caso B: mover la cámara
El objeto sigue en el origen, pero la vista cambia. En OpenGL fijo esto se logra aplicando al mundo la transformación inversa de la cámara. Por eso el signo y el orden de `glRotatef` y `glTranslatef` cambian el resultado.

## Misión 1: El Espejo de la Matriz
### Evidencia 1: objeto rota
![Objeto rota](m1_objeto_rota.png)

### Evidencia 2: cámara orbita
![Cámara orbita](m1_camara_orbita.png)

### Implementación usada
- `renderizar_objeto_rotando(angulo_grados)`: fija la cámara con `glTranslatef(0, 0, -DISTANCIA_CAMARA_Z)` y luego rota el objeto con `glRotatef(angulo_grados, 0, 1, 0)`.
- `renderizar_camara_orbitando(angulo_grados)`: primero aplica `glRotatef(-angulo_grados, 0, 1, 0)` y después `glTranslatef(0, 0, -DISTANCIA_CAMARA_Z)` para simular la órbita de la cámara alrededor del origen.

### Comparación visual
En el modo objeto, la esfera parece girar sobre sí misma mientras la cámara permanece inmóvil. En el modo cámara, la esfera queda estable en el origen y lo que cambia es el punto de vista, por lo que el observador la rodea.

### Orden y signo de las transformaciones
El orden importa porque las transformaciones matriciales no conmutan. Traducir y luego rotar no produce el mismo resultado que rotar y luego traducir. En el caso de la cámara, además, se usa la transformación inversa del movimiento deseado; por eso la rotación de la vista se implementa con `-angulo_grados`.

## Misión 2: El Ojo Declarativo
### Evidencia
![LookAt órbita](m2_lookat_orbita.png)

### Implementación usada
La función `renderizar_con_lookat(angulo_grados)` calcula la posición del ojo en una órbita circular de radio `5.0`:

```python
angulo_radianes = math.radians(angulo_grados)
ojo_x = RADIO_ORBITA_CAMARA * math.sin(angulo_radianes)
ojo_z = RADIO_ORBITA_CAMARA * math.cos(angulo_radianes)
```

Luego define la cámara con:

```python
gluLookAt(ojo_x, 0.0, ojo_z,
          0.0, 0.0, 0.0,
          0.0, 1.0, 0.0)
```

### Observación
`gluLookAt` permite describir la cámara de forma más semántica: ojo, objetivo y vector arriba. Esto evita pensar manualmente en el orden de varias transformaciones y hace más legible la intención del código.

## Misión 3: La Brújula de Luces
### Configuración
Para esta misión se debe activar:

```python
USAR_ILUMINACION = True
```

La luz se activa en `configurar_iluminacion_basica()`, pero su dirección se posiciona fotograma a fotograma con `posicionar_luz_direccional()`. Lo importante es recordar que `GL_POSITION` se interpreta usando la matriz `MODELVIEW` activa en el momento de definir la luz.

### Observación esperada
En esta implementación, en modo objeto la luz se fija después de colocar la cámara pero antes de rotar la esfera, así que queda anclada al frame de la cámara. En modo cámara, la luz se fija después de construir la vista orbital, por lo que se comporta como una luz estable respecto al mundo observado. El resultado es que el patrón de sombreado cambia de forma distinta en cada modo.

### Evidencias opcionales
![Luz con objeto rotando](m3_luz_objeto.png)

![Luz con cámara orbitando](m3_luz_camara.png)

## Análisis del Analista (Reflexiones Finales)
1. **Orden de matrices:** ¿Por qué en OpenGL fijo el orden en que escribes `glTranslatef` y `glRotatef` cambia el resultado aunque uses los mismos números?
   Porque cada transformación modifica el sistema de referencia de la siguiente. Las matrices de traslación y rotación no conmutan, así que cambiar el orden altera tanto la posición final como el eje alrededor del cual ocurre el movimiento.

2. **Objeto vs cámara:** En la práctica, ¿cuándo prefieres rotar el modelo y cuándo orbitar la cámara?
   Conviene rotar el modelo cuando se quiere mostrar su forma o animación propia. Conviene orbitar la cámara cuando el objeto debe permanecer estable en el mundo y lo que interesa es inspeccionarlo desde distintos puntos de vista.

3. **gluLookAt vs translate+rotate:** ¿Qué ventaja tiene describir la cámara con ojo, objetivo y arriba para equipos de desarrollo?
   Hace el código más expresivo y menos propenso a errores de signo u orden. También facilita comunicar la intención entre integrantes del equipo porque la cámara se define con conceptos geométricos directos.

4. **Luces:** Si la luz se define en el frame de la cámara sin reubicarla al mundo, ¿qué artefacto visual esperas al rotar solo el objeto?
   El sombreado puede verse incoherente, como si la luz se moviera junto con el observador. Eso hace que las zonas iluminadas y en sombra no correspondan a una fuente fija en el espacio de la escena.
