import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt
from PIL import Image
import sys

keys = {}
camera_pos = [4.0, 4.0, 8.0]
camera_speed = 0.1

textures = {}


def load_texture(name, path):
    img = Image.open(path).convert("RGB")
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = img.tobytes()

    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                 img.width, img.height, 0,
                 GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, 0)
    textures[name] = tex_id

def key_callback(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        keys[key] = True
    elif action == glfw.RELEASE:
        keys[key] = False

def init():
    glClearColor(0.5, 0.8, 1.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, 1.0, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    load_texture("grass", "grass.jpg")
    load_texture("wood", "wood.jpg")
    load_texture("sky", "sky.jpg")

def draw_cube():
    glBindTexture(GL_TEXTURE_2D, textures["wood"])
    glColor3f(1, 1, 1)
    glBegin(GL_QUADS)

    glTexCoord2f(0, 0); glVertex3f(-1, 0,  1)  # Frente
    glTexCoord2f(1, 0); glVertex3f( 1, 0,  1)
    glTexCoord2f(1, 1); glVertex3f( 1, 1,  1)
    glTexCoord2f(0, 1); glVertex3f(-1, 1,  1)

    glTexCoord2f(0, 0); glVertex3f( 1, 0, -1)  # Atrás
    glTexCoord2f(1, 0); glVertex3f(-1, 0, -1)
    glTexCoord2f(1, 1); glVertex3f(-1, 1, -1)
    glTexCoord2f(0, 1); glVertex3f( 1, 1, -1)

    glTexCoord2f(0, 0); glVertex3f(-1, 0, -1)  # Izquierda
    glTexCoord2f(1, 0); glVertex3f(-1, 0,  1)
    glTexCoord2f(1, 1); glVertex3f(-1, 1,  1)
    glTexCoord2f(0, 1); glVertex3f(-1, 1, -1)

    glTexCoord2f(0, 0); glVertex3f( 1, 0,  1)  # Derecha
    glTexCoord2f(1, 0); glVertex3f( 1, 0, -1)
    glTexCoord2f(1, 1); glVertex3f( 1, 1, -1)
    glTexCoord2f(0, 1); glVertex3f( 1, 1,  1)

    glTexCoord2f(0, 0); glVertex3f(-1, 1,  1)  # Arriba
    glTexCoord2f(1, 0); glVertex3f( 1, 1,  1)
    glTexCoord2f(1, 1); glVertex3f( 1, 1, -1)
    glTexCoord2f(0, 1); glVertex3f(-1, 1, -1)

    glTexCoord2f(0, 0); glVertex3f(-1, 0, -1)  # Abajo
    glTexCoord2f(1, 0); glVertex3f( 1, 0, -1)
    glTexCoord2f(1, 1); glVertex3f( 1, 0,  1)
    glTexCoord2f(0, 1); glVertex3f(-1, 0,  1)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)

def draw_roof():
    glBindTexture(GL_TEXTURE_2D, textures["sky"])
    glColor3f(1, 1, 1)
    glBegin(GL_TRIANGLES)

    glTexCoord2f(0, 0); glVertex3f(-1, 1,  1)  # Frente
    glTexCoord2f(1, 0); glVertex3f( 1, 1,  1)
    glTexCoord2f(0.5, 1); glVertex3f(0, 2, 0)

    glTexCoord2f(0, 0); glVertex3f( 1, 1, -1)  # Atrás
    glTexCoord2f(1, 0); glVertex3f(-1, 1, -1)
    glTexCoord2f(0.5, 1); glVertex3f(0, 2, 0)

    glTexCoord2f(0, 0); glVertex3f(-1, 1, -1)  # Izquierda
    glTexCoord2f(1, 0); glVertex3f(-1, 1,  1)
    glTexCoord2f(0.5, 1); glVertex3f(0, 2, 0)

    glTexCoord2f(0, 0); glVertex3f( 1, 1,  1)  # Derecha
    glTexCoord2f(1, 0); glVertex3f( 1, 1, -1)
    glTexCoord2f(0.5, 1); glVertex3f(0, 2, 0)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)

def draw_house(x=0.0, z=0.0):
    glPushMatrix()
    glTranslatef(x, 0.0, z)
    draw_cube()
    draw_roof()
    glPopMatrix()

def draw_ground(size=20):
    glBindTexture(GL_TEXTURE_2D, textures["grass"])
    glColor3f(1, 1, 1)
    s = size / 2
    scale = 5
    glBegin(GL_QUADS)
    glTexCoord2f(0,     0);     glVertex3f(-s, 0,  s)
    glTexCoord2f(scale, 0);     glVertex3f( s, 0,  s)
    glTexCoord2f(scale, scale); glVertex3f( s, 0, -s)
    glTexCoord2f(0,     scale); glVertex3f(-s, 0, -s)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)

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
