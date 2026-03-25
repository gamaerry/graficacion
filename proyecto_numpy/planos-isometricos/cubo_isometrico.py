import cv2 as cv
import numpy as np


def iso(x, y, z, origin, scale=60):
    ox, oy = origin
    sx = ox + (x - y) * scale
    sy = oy + (x + y) * (scale // 2) - z * scale
    return int(sx), int(sy)


def main():
    img = np.full((500, 700, 3), 245, dtype=np.uint8)
    origin = (350, 250)
    scale = 80

    # Vertices visibles del cubo 1x1x1
    top = np.array([
        iso(0, 0, 1, origin, scale),
        iso(1, 0, 1, origin, scale),
        iso(1, 1, 1, origin, scale),
        iso(0, 1, 1, origin, scale),
    ], dtype=np.int32)

    left = np.array([
        iso(0, 1, 1, origin, scale),
        iso(0, 0, 1, origin, scale),
        iso(0, 0, 0, origin, scale),
        iso(0, 1, 0, origin, scale),
    ], dtype=np.int32)

    right = np.array([
        iso(1, 0, 1, origin, scale),
        iso(1, 1, 1, origin, scale),
        iso(1, 1, 0, origin, scale),
        iso(1, 0, 0, origin, scale),
    ], dtype=np.int32)

    # cv.fillConvexPoly(img, top, (220, 220, 250), cv.LINE_AA)
    # cv.fillConvexPoly(img, left, (170, 170, 220), cv.LINE_AA)
    # cv.fillConvexPoly(img, right, (120, 120, 185), cv.LINE_AA)

    cv.polylines(img, [top], True, (40, 40, 40), 2, cv.LINE_AA)
    cv.polylines(img, [left], True, (40, 40, 40), 2, cv.LINE_AA)
    cv.polylines(img, [right], True, (40, 40, 40), 2, cv.LINE_AA)

    cv.putText(
        img,
        "Cubo isometrico",
        (30, 40),
        cv.FONT_HERSHEY_SIMPLEX,
        0.9,
        (40, 40, 40),
        2,
        cv.LINE_AA,
    )

    cv.imwrite("cubo_isometrico.png", img)
    cv.imshow("cubo", img)
    cv.waitKey(0)
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
