import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt
import sys

keys = {}
camera_pos = [4.0, 4.0, 8.0]
camera_speed = 0.1

def key_callback(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        keys[key] = True
    elif action == glfw.RELEASE:
        keys[key] = False

def init():
    glClearColor(0.5, 0.8, 1.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, 1.0, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def draw_cube():
    glBegin(GL_QUADS)
    glColor3f(0.8, 0.5, 0.2)

    glVertex3f(-1, 0,  1); glVertex3f( 1, 0,  1)  # Frente
    glVertex3f( 1, 1,  1); glVertex3f(-1, 1,  1)

    glVertex3f(-1, 0, -1); glVertex3f( 1, 0, -1)  # Atrás
    glVertex3f( 1, 1, -1); glVertex3f(-1, 1, -1)

    glVertex3f(-1, 0, -1); glVertex3f(-1, 0,  1)  # Izquierda
    glVertex3f(-1, 1,  1); glVertex3f(-1, 1, -1)

    glVertex3f( 1, 0, -1); glVertex3f( 1, 0,  1)  # Derecha
    glVertex3f( 1, 1,  1); glVertex3f( 1, 1, -1)

    glColor3f(0.9, 0.6, 0.3)
    glVertex3f(-1, 1, -1); glVertex3f( 1, 1, -1)  # Arriba
    glVertex3f( 1, 1,  1); glVertex3f(-1, 1,  1)

    glColor3f(0.6, 0.4, 0.2)
    glVertex3f(-1, 0, -1); glVertex3f( 1, 0, -1)  # Abajo
    glVertex3f( 1, 0,  1); glVertex3f(-1, 0,  1)
    glEnd()

def draw_roof():
    glBegin(GL_TRIANGLES)
    glColor3f(0.9, 0.1, 0.1)

    glVertex3f(-1, 1,  1); glVertex3f( 1, 1,  1); glVertex3f(0, 2, 0)  # Frente
    glVertex3f(-1, 1, -1); glVertex3f( 1, 1, -1); glVertex3f(0, 2, 0)  # Atrás
    glVertex3f(-1, 1, -1); glVertex3f(-1, 1,  1); glVertex3f(0, 2, 0)  # Izquierda
    glVertex3f( 1, 1, -1); glVertex3f( 1, 1,  1); glVertex3f(0, 2, 0)  # Derecha
    glEnd()

def draw_house(x=0.0, z=0.0):
    glPushMatrix()
    glTranslatef(x, 0.0, z)
    draw_cube()
    draw_roof()
    glPopMatrix()

def draw_ground(size=20):
    glBegin(GL_QUADS)
    glColor3f(0.3, 0.3, 0.3)
    s = size / 2
    glVertex3f(-s, 0,  s); glVertex3f( s, 0,  s)
    glVertex3f( s, 0, -s); glVertex3f(-s, 0, -s)
    glEnd()

def draw_scene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
              0, 1, 0,
              0, 1, 0)

    draw_ground()
    draw_house()
    draw_house(4, 0)         
    draw_house(8, 0)
    draw_house(0, 5)

    glfw.swap_buffers(window)

def process_input():
    global camera_pos

    if keys.get(glfw.KEY_W, False):
        camera_pos[2] -= camera_speed
    if keys.get(glfw.KEY_S, False):
        camera_pos[2] += camera_speed
    if keys.get(glfw.KEY_A, False):
        camera_pos[0] -= camera_speed
    if keys.get(glfw.KEY_D, False):
        camera_pos[0] += camera_speed
    if keys.get(glfw.KEY_UP, False):
        camera_pos[1] += camera_speed
    if keys.get(glfw.KEY_DOWN, False):
        camera_pos[1] -= camera_speed

def main():
    global window

    if not glfw.init():
        sys.exit()

    width, height = 800, 600
    window = glfw.create_window(width, height, "Casa 3D", None, None)
    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glViewport(0, 0, width, height)
    init()

    while not glfw.window_should_close(window):
        draw_scene()
        glfw.poll_events()
        process_input()

    glfw.terminate()

if __name__ == "__main__":
    main()
