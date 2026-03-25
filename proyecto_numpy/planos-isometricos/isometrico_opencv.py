import cv2 as cv
import numpy as np


WIDTH = 1000
HEIGHT = 700
BACKGROUND = (245, 245, 240)


def iso(x, y, z, origin, scale=32):
    """Proyeccion isometrica basica de 3D discreto a 2D."""
    ox, oy = origin
    sx = ox + (x - y) * scale
    sy = oy + (x + y) * (scale // 2) - z * scale
    return int(sx), int(sy)


def draw_grid(img, rows, cols, origin, scale=32, color=(190, 190, 190)):
    for x in range(rows + 1):
        p1 = iso(x, 0, 0, origin, scale)
        p2 = iso(x, cols, 0, origin, scale)
        cv.line(img, p1, p2, color, 1, cv.LINE_AA)

    for y in range(cols + 1):
        p1 = iso(0, y, 0, origin, scale)
        p2 = iso(rows, y, 0, origin, scale)
        cv.line(img, p1, p2, color, 1, cv.LINE_AA)


def fill_face(img, points, color):
    pts = np.array(points, dtype=np.int32)
    cv.fillConvexPoly(img, pts, color, cv.LINE_AA)
    cv.polylines(img, [pts], True, (45, 45, 45), 2, cv.LINE_AA)


def draw_box(img, x, y, z, w, d, h, origin, scale=32,
             top=(205, 225, 245), left=(150, 180, 215), right=(110, 145, 190)):
    # Cara superior
    a = iso(x, y, z + h, origin, scale)
    b = iso(x + w, y, z + h, origin, scale)
    c = iso(x + w, y + d, z + h, origin, scale)
    d1 = iso(x, y + d, z + h, origin, scale)

    # Cara izquierda
    e = iso(x, y + d, z, origin, scale)
    f = iso(x, y, z, origin, scale)

    # Cara derecha
    g = iso(x + w, y, z, origin, scale)
    h1 = iso(x + w, y + d, z, origin, scale)

    fill_face(img, [a, b, c, d1], top)
    fill_face(img, [d1, a, f, e], left)
    fill_face(img, [b, c, h1, g], right)


def draw_column(img, x, y, floors, origin, scale=32):
    for i in range(floors):
        draw_box(
            img,
            x=x,
            y=y,
            z=i,
            w=1,
            d=1,
            h=1,
            origin=origin,
            scale=scale,
            top=(220 - i * 10, 210 - i * 8, 180 - i * 6),
            left=(185 - i * 8, 170 - i * 7, 145 - i * 5),
            right=(145 - i * 7, 130 - i * 6, 110 - i * 5),
        )


def main():
    img = np.full((HEIGHT, WIDTH, 3), BACKGROUND, dtype=np.uint8)
    origin = (WIDTH // 2, 180)

    draw_grid(img, rows=8, cols=8, origin=origin, scale=40)

    # Plataforma base
    draw_box(
        img,
        x=1,
        y=1,
        z=0,
        w=4,
        d=3,
        h=1,
        origin=origin,
        scale=40,
        top=(210, 235, 210),
        left=(165, 205, 165),
        right=(120, 175, 120),
    )

    # Dos volumenes sobre la plataforma
    draw_box(
        img,
        x=1,
        y=1,
        z=1,
        w=2,
        d=2,
        h=2,
        origin=origin,
        scale=40,
        top=(220, 220, 245),
        left=(175, 180, 220),
        right=(125, 135, 185),
    )

    draw_box(
        img,
        x=3,
        y=2,
        z=1,
        w=2,
        d=1,
        h=3,
        origin=origin,
        scale=40,
        top=(245, 220, 210),
        left=(220, 175, 160),
        right=(180, 130, 115),
    )

    # Columna decorativa
    draw_column(img, x=5, y=1, floors=3, origin=origin, scale=40)

    cv.putText(
        img,
        "Plano isometrico con primitivas de OpenCV",
        (30, 40),
        cv.FONT_HERSHEY_SIMPLEX,
        0.8,
        (40, 40, 40),
        2,
        cv.LINE_AA,
    )

    cv.imwrite("plano_isometrico.png", img)
    cv.imshow("isometrico", img)
    cv.waitKey(0)
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
