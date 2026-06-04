#!/usr/bin/env python3
"""
Realidad aumentada del campus usando un marcador ArUco.

Usa el marcador ArUco ID=0 como referencia y ancla el mapa 3D de itm.py
sobre el plano del marcador.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import glfw
import numpy as np
from OpenGL.GL import *

import itm


CAMERA_INDEX = 0
MARKER_LENGTH_M = 0.10
ARUCO_DICT = cv2.aruco.DICT_4X4_50
MARKER_ID = 1
MAP_SCALE = 0.006
WINDOW_TITLE = "RA: marcador ArUco + mapa ITM (ESC=salir)"
ZNear, ZFar = 0.01, 100.0

SCRIPT_DIR = Path(__file__).resolve().parent
CALIB_NPZ = SCRIPT_DIR / "camera_ar.npz"


def default_camera_matrix(width: int, height: int) -> np.ndarray:
    f = float(max(width, height))
    cx, cy = width / 2.0, height / 2.0
    return np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]], dtype=np.float64)


def load_calibration(width: int, height: int):
    if CALIB_NPZ.is_file():
        data = np.load(CALIB_NPZ)
        return data["camera_matrix"], data["dist_coeffs"]
    return default_camera_matrix(width, height), np.zeros((5, 1), dtype=np.float64)


def make_aruco_detector():
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    params = cv2.aruco.DetectorParameters()
    if hasattr(cv2.aruco, "ArucoDetector"):
        return cv2.aruco.ArucoDetector(dictionary, params), dictionary
    return None, dictionary


def detect_marker(gray, detector, dictionary):
    if detector is not None:
        corners, ids, _ = detector.detectMarkers(gray)
    else:
        corners, ids, _ = cv2.aruco.detectMarkers(
            gray, dictionary, parameters=cv2.aruco.DetectorParameters()
        )
    if ids is None or len(ids) == 0:
        return None, None, None
    idx = 0
    if MARKER_ID is not None:
        matches = np.where(ids.flatten() == MARKER_ID)[0]
        if len(matches) == 0:
            return None, None, None
        idx = int(matches[0])
    return corners[idx], ids[idx], idx


def marker_object_points(side_length):
    s = side_length / 2.0
    return np.array([[-s, s, 0], [s, s, 0], [s, -s, 0], [-s, -s, 0]], dtype=np.float32)


def projection_from_k(K, width, height, znear, zfar):
    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]
    P = np.zeros((4, 4), dtype=np.float32)
    P[0, 0] = 2.0 * fx / width
    P[1, 1] = 2.0 * fy / height
    P[0, 2] = (width - 2.0 * cx) / width
    P[1, 2] = (2.0 * cy - height) / height
    P[2, 2] = -(zfar + znear) / (zfar - znear)
    P[2, 3] = -1.0
    P[3, 2] = -2.0 * zfar * znear / (zfar - znear)
    return P


def modelview_from_pose(rvec, tvec) -> np.ndarray:
    R, _ = cv2.Rodrigues(rvec)
    M = np.eye(4, dtype=np.float64)
    M[:3, :3] = R
    M[:3, 3] = tvec.flatten()
    cv_to_gl = np.diag([1.0, -1.0, -1.0, 1.0])
    return (cv_to_gl @ M).T.astype(np.float32)





_tex_id = None
_tex_buf = None


def upload_frame_texture(frame_bgr, width, height) -> None:
    global _tex_id, _tex_buf
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    rgb = cv2.flip(rgb, 0)
    if _tex_buf is None or _tex_buf.shape[:2] != (height, width):
        _tex_buf = np.empty((height, width, 3), dtype=np.uint8)
    np.copyto(_tex_buf, rgb)
    if _tex_id is None:
        _tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, _tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, _tex_buf)


def draw_background_quad(width, height) -> None:
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, _tex_id)
    glColor3f(1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(0, 0)
    glTexCoord2f(1, 0)
    glVertex2f(width, 0)
    glTexCoord2f(1, 1)
    glVertex2f(width, height)
    glTexCoord2f(0, 1)
    glVertex2f(0, height)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)


def estimate_pose(corners, camera_matrix, dist_coeffs):
    image_points = corners[0] if corners.ndim == 3 else corners
    image_points = np.asarray(image_points, dtype=np.float32).reshape(-1, 2)
    obj_pts = marker_object_points(MARKER_LENGTH_M)
    flags = cv2.SOLVEPNP_IPPE_SQUARE if hasattr(cv2, "SOLVEPNP_IPPE_SQUARE") else cv2.SOLVEPNP_ITERATIVE
    ok, rvec, tvec = cv2.solvePnP(obj_pts, image_points, camera_matrix, dist_coeffs, flags=flags)
    if not ok:
        return None, None
    return rvec, tvec


def draw_itm_map_on_marker(rvec, tvec, camera_matrix, width, height) -> None:
    P = projection_from_k(camera_matrix, width, height, ZNear, ZFar)
    MV = modelview_from_pose(rvec, tvec)

    glMatrixMode(GL_PROJECTION)
    glLoadMatrixf(P)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glMultMatrixf(MV)

    glDisable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glPushMatrix()
    glScalef(MAP_SCALE, MAP_SCALE, MAP_SCALE)
    glRotatef(90.0, 1.0, 0.0, 0.0)
    itm.draw_campus_base()
    itm.draw_sports_fields()
    itm.draw_campus_fences()
    itm.draw_buildings()
    itm.draw_trees()
    glPopMatrix()


def main() -> None:
    detector, dictionary = make_aruco_detector()

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("No se pudo abrir la camara.", file=sys.stderr)
        sys.exit(1)

    ret, probe = cap.read()
    if not ret:
        print("No se pudo leer la camara.", file=sys.stderr)
        sys.exit(1)

    cam_h, cam_w = probe.shape[:2]
    camera_matrix, dist_coeffs = load_calibration(cam_w, cam_h)

    if not glfw.init():
        sys.exit(1)

    window = glfw.create_window(cam_w, cam_h, WINDOW_TITLE, None, None)
    if not window:
        glfw.terminate()
        sys.exit(1)

    glfw.make_context_current(window)
    glfw.swap_interval(1)

    def on_key(win, key, _scancode, action, _mods):
        if action == glfw.PRESS and key in (glfw.KEY_ESCAPE, glfw.KEY_Q):
            glfw.set_window_should_close(win, True)

    glfw.set_key_callback(window, on_key)
    glEnable(GL_DEPTH_TEST)

    while not glfw.window_should_close(window):
        ret, frame = cap.read()
        if not ret:
            continue

        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, _, _ = detect_marker(gray, detector, dictionary)

        if corners is not None:
            pts = corners.astype(np.int32).reshape(-1, 1, 2)
            cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
            cv2.putText(frame, "ArUco detectado", (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        glViewport(0, 0, w, h)
        upload_frame_texture(frame, w, h)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_background_quad(w, h)

        if corners is not None:
            rvec, tvec = estimate_pose(corners, camera_matrix, dist_coeffs)
            if rvec is not None:
                draw_itm_map_on_marker(rvec, tvec, camera_matrix, w, h)

        glfw.swap_buffers(window)
        glfw.poll_events()

    cap.release()
    glfw.terminate()


if __name__ == "__main__":
    main()
