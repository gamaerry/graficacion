#!/usr/bin/env python3
"""
Operación Órbita Dual
=====================

Ejemplo funcional con GLFW + PyOpenGL usando pipeline fijo.
La esfera se dibuja con GLU (`gluSphere`), sin GLUT.

Instalación:
  pip install PyOpenGL PyOpenGL_accelerate glfw

Controles:
  1  Rotar objeto (cámara fija)
  2  Orbitar cámara (objeto fijo)
  3  Orbitar cámara con gluLookAt
  ESC o Q  Salir

Misiones sugeridas:
  - Misión 1: compara el orden de transformaciones en modo objeto y modo cámara.
  - Misión 2: usa `gluLookAt` para describir la cámara declarativamente.
  - Misión 3: activa la iluminación y observa cómo cambia según el frame de referencia.
"""

from __future__ import annotations

import math
import sys

import glfw
from OpenGL.GL import *
from OpenGL.GLU import (
    GLU_FILL,
    gluLookAt,
    gluNewQuadric,
    gluPerspective,
    gluQuadricDrawStyle,
    gluSphere,
)


# ---------------------------------------------------------------------------
# Configuración general
# ---------------------------------------------------------------------------
TITULO_VENTANA = "Orbita Dual (GLFW) - 1/2/3 cambia modo"
ANCHO_VENTANA = 800
ALTO_VENTANA = 600

MODO_ROTAR_OBJETO = 1
MODO_ORBITAR_CAMARA = 2
MODO_LOOKAT = 3
MODO_INICIAL = MODO_ROTAR_OBJETO

RADIO_ORBITA_CAMARA = 5.0
DISTANCIA_CAMARA_Z = 5.0
VELOCIDAD_ANGULAR = 0.6

USAR_ILUMINACION = True


# ---------------------------------------------------------------------------
# Recursos OpenGL
# ---------------------------------------------------------------------------
cuadrica_esfera = None


def obtener_cuadrica_esfera():
    """Crea la cuádrica una sola vez y la reutiliza."""
    global cuadrica_esfera
    if cuadrica_esfera is None:
        cuadrica_esfera = gluNewQuadric()
        gluQuadricDrawStyle(cuadrica_esfera, GLU_FILL)
    return cuadrica_esfera


def dibujar_esfera(radio: float = 1.0) -> None:
    """Dibuja la esfera principal de la escena."""
    gluSphere(obtener_cuadrica_esfera(), radio, 40, 24)


def configurar_iluminacion_basica() -> None:
    """
    Define una luz simple.

    La posición se interpreta en el sistema de referencia activo en el momento
    de llamar `glLightfv(GL_POSITION, ...)`, por eso sirve para experimentar
    en la Misión 3.
    """
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    luz_ambiente = [0.2, 0.2, 0.2, 1.0]
    luz_difusa = [0.9, 0.9, 0.85, 1.0]

    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)


def posicionar_luz_direccional() -> None:
    """
    Coloca una luz direccional.

    La posición/dirección queda expresada en el sistema de referencia definido
    por la matriz MODELVIEW activa en este instante.
    """
    posicion_luz = [0.5, 0.8, 1.0, 0.0]
    glLightfv(GL_LIGHT0, GL_POSITION, posicion_luz)


# ---------------------------------------------------------------------------
# Utilidades de transformación y escena
# ---------------------------------------------------------------------------
def preparar_matriz_modelo_vista() -> None:
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def colorear_esfera(color_rgb: tuple[float, float, float]) -> None:
    glColor3f(*color_rgb)


def dibujar_esfera_principal(color_rgb: tuple[float, float, float]) -> None:
    colorear_esfera(color_rgb)
    dibujar_esfera(1.0)


def renderizar_objeto_rotando(angulo_grados: float) -> None:
    """
    Modo 1:
    La cámara queda fija y el objeto rota sobre su eje Y.
    """
    preparar_matriz_modelo_vista()
    glTranslatef(0.0, 0.0, -DISTANCIA_CAMARA_Z)
    if USAR_ILUMINACION:
        # La luz queda anclada al frame de la camara antes de rotar el objeto.
        posicionar_luz_direccional()
    glRotatef(angulo_grados, 0.0, 1.0, 0.0)
    dibujar_esfera_principal((0.35, 0.65, 1.0))


def renderizar_camara_orbitando(angulo_grados: float) -> None:
    """
    Modo 2:
    El objeto permanece en el origen y la cámara aparenta orbitarlo.

    En pipeline fijo esto se implementa aplicando la transformación inversa
    al mundo: primero se rota la vista y luego se aleja la cámara.
    """
    preparar_matriz_modelo_vista()
    glRotatef(-angulo_grados, 0.0, 1.0, 0.0)
    glTranslatef(0.0, 0.0, -DISTANCIA_CAMARA_Z)
    if USAR_ILUMINACION:
        # La vista ya esta colocada; la luz queda fija al mundo observado.
        posicionar_luz_direccional()
    dibujar_esfera_principal((1.0, 0.55, 0.35))


def renderizar_camara_orbitando_variante_b(angulo_grados: float) -> None:
    """
    Variante útil para comparar orden de transformaciones.

    Aquí se traslada primero y luego se rota. Visualmente no representa la
    misma relación cámara-objeto que `renderizar_camara_orbitando`.
    """
    preparar_matriz_modelo_vista()
    glTranslatef(0.0, 0.0, -DISTANCIA_CAMARA_Z)
    glRotatef(angulo_grados, 0.0, 1.0, 0.0)
    if USAR_ILUMINACION:
        posicionar_luz_direccional()
    dibujar_esfera_principal((0.45, 1.0, 0.45))


def renderizar_con_lookat(angulo_grados: float) -> None:
    """
    Modo 3:
    La cámara se define mediante ojo, objetivo y vector arriba.
    """
    preparar_matriz_modelo_vista()

    angulo_radianes = math.radians(angulo_grados)
    ojo_x = RADIO_ORBITA_CAMARA * math.sin(angulo_radianes)
    ojo_z = RADIO_ORBITA_CAMARA * math.cos(angulo_radianes)

    gluLookAt(
        ojo_x,
        0.0,
        ojo_z,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
    )
    if USAR_ILUMINACION:
        posicionar_luz_direccional()
    dibujar_esfera_principal((0.95, 0.85, 0.35))


def renderizar_segun_modo(modo_actual: int, angulo_grados: float) -> None:
    if modo_actual == MODO_ROTAR_OBJETO:
        renderizar_objeto_rotando(angulo_grados)
    elif modo_actual == MODO_ORBITAR_CAMARA:
        renderizar_camara_orbitando(angulo_grados)
        # Para comparar la variante alternativa, comenta la línea anterior
        # y descomenta la siguiente:
        # renderizar_camara_orbitando_variante_b(angulo_grados)
    else:
        renderizar_con_lookat(angulo_grados)


def configurar_proyeccion(ancho_framebuffer: int, alto_framebuffer: int) -> None:
    glViewport(0, 0, ancho_framebuffer, alto_framebuffer)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50.0, ancho_framebuffer / float(alto_framebuffer), 0.1, 100.0)


def preparar_fotograma(ancho_framebuffer: int, alto_framebuffer: int) -> None:
    if alto_framebuffer <= 0:
        alto_framebuffer = 1
    configurar_proyeccion(ancho_framebuffer, alto_framebuffer)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


def actualizar_angulo(angulo_actual: float) -> float:
    nuevo_angulo = angulo_actual + VELOCIDAD_ANGULAR
    if nuevo_angulo >= 360.0:
        nuevo_angulo -= 360.0
    return nuevo_angulo


# ---------------------------------------------------------------------------
# GLFW
# ---------------------------------------------------------------------------
def inicializar_glfw() -> None:
    if not glfw.init():
        print("Error: no se pudo inicializar GLFW", file=sys.stderr)
        sys.exit(1)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)


def crear_ventana() -> glfw._GLFWwindow:
    ventana = glfw.create_window(ANCHO_VENTANA, ALTO_VENTANA, TITULO_VENTANA, None, None)
    if not ventana:
        glfw.terminate()
        print("Error: no se pudo crear la ventana OpenGL", file=sys.stderr)
        sys.exit(1)

    glfw.make_context_current(ventana)
    glfw.swap_interval(1)
    return ventana


def registrar_controles(ventana: glfw._GLFWwindow) -> dict[str, int]:
    estado = {"modo_actual": MODO_INICIAL}

    def al_presionar_tecla(ventana_actual, tecla, scancode, accion, mods):
        del scancode, mods
        if accion != glfw.PRESS:
            return
        if tecla in (glfw.KEY_ESCAPE, glfw.KEY_Q):
            glfw.set_window_should_close(ventana_actual, True)
        elif tecla == glfw.KEY_1:
            estado["modo_actual"] = MODO_ROTAR_OBJETO
        elif tecla == glfw.KEY_2:
            estado["modo_actual"] = MODO_ORBITAR_CAMARA
        elif tecla == glfw.KEY_3:
            estado["modo_actual"] = MODO_LOOKAT

    glfw.set_key_callback(ventana, al_presionar_tecla)
    return estado


def configurar_estado_opengl() -> None:
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.08, 0.08, 0.12, 1.0)

    if USAR_ILUMINACION:
        configurar_iluminacion_basica()
    else:
        glDisable(GL_LIGHTING)


def ejecutar_bucle_principal(ventana: glfw._GLFWwindow, estado: dict[str, int]) -> None:
    angulo_actual = 0.0

    while not glfw.window_should_close(ventana):
        ancho_framebuffer, alto_framebuffer = glfw.get_framebuffer_size(ventana)
        preparar_fotograma(ancho_framebuffer, alto_framebuffer)
        renderizar_segun_modo(estado["modo_actual"], angulo_actual)

        angulo_actual = actualizar_angulo(angulo_actual)

        glfw.swap_buffers(ventana)
        glfw.poll_events()


def main() -> None:
    inicializar_glfw()
    ventana = crear_ventana()
    estado = registrar_controles(ventana)
    configurar_estado_opengl()

    try:
        ejecutar_bucle_principal(ventana, estado)
    finally:
        glfw.terminate()


if __name__ == "__main__":
    main()
