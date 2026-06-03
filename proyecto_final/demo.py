import argparse
import math
import time
from pathlib import Path

import cv2
import numpy as np


W, H = 800, 600
FPS = 30
DURATION = 48.0
SCENE_COUNT = 6
TRANSITION = 1.25


def clamp01(x):
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def smoothstep(a, b, x):
    x = clamp01((x - a) / (b - a))
    return x * x * (3.0 - 2.0 * x)


def hsv_to_bgr(h, s=220, v=245):
    hsv = np.uint8([[[int(h) % 180, int(np.clip(s, 0, 255)), int(np.clip(v, 0, 255))]]])
    return tuple(int(c) for c in cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0])


def poly_param(fx, fy, t0, t1, n, cx, cy, sx, sy):
    ts = np.linspace(t0, t1, n, dtype=np.float32)
    xs = fx(ts) * sx + cx
    ys = fy(ts) * sy + cy
    return np.round(np.stack([xs, ys], axis=1)).astype(np.int32).reshape((-1, 1, 2))


def regular_polygon(cx, cy, radius, sides, angle=0.0):
    pts = []
    for i in range(sides):
        a = angle + i * 2.0 * math.pi / sides
        pts.append([cx + radius * math.cos(a), cy + radius * math.sin(a)])
    return np.round(np.array(pts, dtype=np.float32)).astype(np.int32).reshape((-1, 1, 2))


def make_state():
    rng = np.random.default_rng(2026)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (xx - W * 0.5) / (W * 0.5)
    ny = (yy - H * 0.5) / (H * 0.5)
    vignette = np.clip(1.0 - 0.48 * (nx * nx + ny * ny), 0.0, 1.0).astype(np.float32)
    radial = np.clip(1.0 - 1.8 * np.sqrt(nx * nx + ny * ny), 0.0, 1.0).astype(np.float32)
    stars = np.column_stack(
        [
            rng.integers(0, W, 520),
            rng.integers(0, int(H * 0.72), 520),
            rng.integers(90, 255, 520),
        ]
    )
    particles = np.column_stack(
        [
            rng.random(1300) * W,
            rng.random(1300) * H,
            rng.random(1300) * 2.0 * math.pi,
            rng.random(1300) * 1.0,
        ]
    ).astype(np.float32)
    return {
        "vignette": vignette,
        "radial": radial,
        "stars": stars,
        "particles": particles,
        "heat": np.zeros((H, W), np.float32),
        "fire_rng": np.random.default_rng(99),
    }


def background_hsv_gradient(img, t, hue0, hue1, value_floor=35):
    ys = np.linspace(0.0, 1.0, H, dtype=np.float32)
    hsv = np.zeros((H, W, 3), np.uint8)
    hue = hue0 + (hue1 - hue0) * ys + 8.0 * np.sin(t * 0.55 + ys * 5.0)
    sat = 150 + 55 * np.sin(t * 0.22 + ys * 2.2)
    val = value_floor + 150 * (1.0 - ys) + 20 * np.sin(t * 0.35 + ys * 4.0)
    hsv[:, :, 0] = np.clip(hue, 0, 179).astype(np.uint8)[:, None]
    hsv[:, :, 1] = np.clip(sat, 80, 235).astype(np.uint8)[:, None]
    hsv[:, :, 2] = np.clip(val, 25, 235).astype(np.uint8)[:, None]
    img[:] = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def draw_title(img, title, subtitle):
    cv2.putText(img, title, (44, 66), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (245, 245, 245), 2, cv2.LINE_AA)
    cv2.putText(img, subtitle, (46, 96), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (215, 222, 226), 1, cv2.LINE_AA)


def draw_grid(img, t, color):
    horizon = int(H * 0.58)
    for i in range(14):
        y = horizon + int((i / 13.0) ** 1.85 * (H - horizon))
        cv2.line(img, (0, y), (W, y), color, 1, cv2.LINE_AA)
    for i in range(-11, 12):
        x0 = int(W * 0.5 + i * 35 + 18 * math.sin(t + i))
        cv2.line(img, (x0, horizon), (int(W * 0.5 + i * 86), H), color, 1, cv2.LINE_AA)


def draw_neon_polyline(img, pts, color, closed=False, thickness=2):
    glow = np.zeros_like(img)
    cv2.polylines(glow, [pts], closed, color, max(5, thickness * 3), cv2.LINE_AA)
    glow = cv2.GaussianBlur(glow, (0, 0), 4.0)
    cv2.addWeighted(img, 1.0, glow, 0.58, 0.0, img)
    cv2.polylines(img, [pts], closed, color, thickness, cv2.LINE_AA)


def scene_intro(img, t, state):
    background_hsv_gradient(img, t, 150, 108, 28)
    draw_grid(img, t, (42, 86, 102))
    for x, y, v in state["stars"]:
        twinkle = int(np.clip(v + 55 * math.sin(t * 1.7 + x * 0.03), 80, 255))
        img[int(y), int(x)] = (twinkle, twinkle, twinkle)

    n = 3.2 + 0.55 * math.sin(t * 0.7)
    fx = lambda a: np.sign(np.cos(a)) * np.abs(np.cos(a)) ** (2.0 / n)
    fy = lambda a: np.sign(np.sin(a)) * np.abs(np.sin(a)) ** (2.0 / n)
    pts = poly_param(fx, fy, 0, 2 * math.pi, 900, W * 0.5, H * 0.47, 245, 150)
    draw_neon_polyline(img, pts, hsv_to_bgr(126 + 22 * math.sin(t)), True, 2)

    for i in range(7):
        angle = t * 35 + i * 26
        cv2.ellipse(img, (W // 2, int(H * 0.47)), (250, 58 + i * 9), angle, 0, 360, (72, 110, 130), 1, cv2.LINE_AA)
    cv2.circle(img, (W // 2, int(H * 0.47)), 12 + int(3 * math.sin(t * 3)), (245, 245, 245), -1, cv2.LINE_AA)
    draw_title(img, "DEMO PROCEDURAL", "Superelipse + primitivas: line / circle / ellipse / fillPoly")
    cv2.putText(img, "OpenCV + NumPy", (272, 332), cv2.FONT_HERSHEY_SIMPLEX, 0.78, (242, 242, 242), 2, cv2.LINE_AA)


def scene_lissajous(img, t, state):
    background_hsv_gradient(img, t, 16, 58, 42)
    draw_grid(img, t * 0.4, (35, 66, 78))
    a = 3.0 + 0.7 * math.sin(t * 0.47)
    b = 2.0 + 0.6 * math.cos(t * 0.63)
    delta = math.pi * 0.5 + 0.7 * math.sin(t * 0.33)
    pts = poly_param(lambda x: np.sin(a * x + delta), lambda x: np.sin(b * x), 0, 2 * math.pi, 1200, W * 0.5, H * 0.5, 292, 205)
    draw_neon_polyline(img, pts, hsv_to_bgr(22 + 22 * math.sin(t * 0.8), 230, 248), False, 2)

    for i in range(9):
        px = int(W * 0.13 + i * 74)
        py = int(H * 0.83 + 12 * math.sin(t * 2 + i))
        cv2.circle(img, (px, py), 7 + i % 4, hsv_to_bgr(34 + i * 8, 180, 230), -1, cv2.LINE_AA)
        if i > 0:
            cv2.line(img, (px - 74, int(H * 0.83)), (px, py), (90, 130, 120), 1, cv2.LINE_AA)
    draw_title(img, "ESCENA 1: LISSAJOUS", "x=sen(a t + delta), y=sen(b t)")


def scene_rose(img, t, state):
    background_hsv_gradient(img, t, 82, 148, 38)
    layer = np.zeros_like(img)
    k = 5
    turn = t * 0.35
    pts = poly_param(
        lambda th: np.cos(k * th) * np.cos(th + turn),
        lambda th: np.cos(k * th) * np.sin(th + turn),
        0,
        2 * math.pi,
        1500,
        W * 0.5,
        H * 0.46,
        247,
        247,
    )
    draw_neon_polyline(layer, pts, hsv_to_bgr(138 + 18 * math.sin(t * 0.5), 240, 250), True, 2)
    mask = np.zeros((H, W), np.uint8)
    cv2.circle(mask, (W // 2, int(H * 0.46)), 275, 255, -1, cv2.LINE_AA)
    img[:] = np.where(mask[:, :, None] > 0, cv2.addWeighted(img, 0.82, layer, 0.95, 0.0), img)

    for i in range(8):
        cx = int(W * 0.5 + math.cos(t + i * 0.78) * (285 + 10 * math.sin(t)))
        cy = int(H * 0.46 + math.sin(t + i * 0.78) * 205)
        cv2.ellipse(img, (cx, cy), (18, 8), i * 22 + t * 45, 0, 360, (220, 235, 240), 1, cv2.LINE_AA)
    draw_title(img, "ESCENA 2: ROSA POLAR", "r=cos(5 theta), composicion por mascara circular")


def transformed_ship(t):
    ship = np.zeros((180, 240, 3), np.uint8)
    body = np.array([[25, 112], [120, 25], [215, 112], [150, 145], [90, 145]], np.int32).reshape((-1, 1, 2))
    fin_l = np.array([[72, 132], [23, 165], [88, 154]], np.int32).reshape((-1, 1, 2))
    fin_r = np.array([[168, 132], [217, 165], [152, 154]], np.int32).reshape((-1, 1, 2))
    cv2.fillPoly(ship, [body], (38, 190, 226), cv2.LINE_AA)
    cv2.fillPoly(ship, [fin_l, fin_r], (222, 86, 94), cv2.LINE_AA)
    cv2.circle(ship, (120, 87), 19, (250, 250, 238), -1, cv2.LINE_AA)
    cv2.ellipse(ship, (120, 87), (35, 20), 0, 0, 360, (30, 70, 90), 2, cv2.LINE_AA)
    cv2.line(ship, (120, 25), (120, 145), (255, 255, 255), 1, cv2.LINE_AA)

    angle = 30.0 * math.sin(t * 1.2)
    scale = 0.82 + 0.18 * math.sin(t * 1.7)
    rot = cv2.getRotationMatrix2D((120, 90), angle, scale)
    rotated = cv2.warpAffine(ship, rot, (240, 180), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    shear = 0.28 * math.sin(t * 1.05)
    shear_m = np.float32([[1.0, shear, 0.0], [0.0, 1.0, 0.0]])
    return cv2.warpAffine(rotated, shear_m, (240, 180), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)


def scene_spirograph(img, t, state):
    background_hsv_gradient(img, t, 46, 8, 34)
    R, r, d = 8.0, 3.0, 5.0
    w = (R - r) / r
    pts = poly_param(
        lambda x: (R - r) * np.cos(x) + d * np.cos(w * x + 0.5 * np.sin(t)),
        lambda x: (R - r) * np.sin(x) - d * np.sin(w * x + 0.5 * np.cos(t)),
        0,
        14 * math.pi,
        1800,
        W * 0.5,
        H * 0.46,
        27,
        27,
    )
    draw_neon_polyline(img, pts, hsv_to_bgr(8 + 60 * (0.5 + 0.5 * math.sin(t * 0.6)), 235, 250), False, 2)

    ship = transformed_ship(t)
    x0 = int(W * 0.5 - 120 + 190 * math.sin(t * 0.45))
    y0 = int(H * 0.55 - 90 + 52 * math.cos(t * 0.74))
    roi = img[y0 : y0 + 180, x0 : x0 + 240]
    if roi.shape[:2] == ship.shape[:2]:
        mask = cv2.cvtColor(ship, cv2.COLOR_BGR2GRAY)
        mask = cv2.threshold(mask, 8, 255, cv2.THRESH_BINARY)[1]
        blended = cv2.addWeighted(roi, 0.72, ship, 0.95, 0.0)
        roi[:] = np.where(mask[:, :, None] > 0, blended, roi)

    draw_title(img, "ESCENA 3: HIPOTROCOIDE", "Rotacion + escala + shear con matrices afines 2x3")


def scene_lemniscate_particles(img, t, state):
    background_hsv_gradient(img, t, 100, 68, 30)
    particles = state["particles"]
    xs = (particles[:, 0] + 120 * np.sin(particles[:, 1] / 64.0 + t * 1.55) + 30 * np.cos(t + particles[:, 2])) % W
    ys = (particles[:, 1] + 88 * np.cos(particles[:, 0] / 92.0 + t * 1.1) + 24 * np.sin(t * 1.8 + particles[:, 2])) % H
    values = (130 + 100 * particles[:, 3] + 25 * np.sin(t + particles[:, 2])).astype(np.uint8)
    img[ys.astype(np.int32), xs.astype(np.int32)] = np.stack([values, values, np.full_like(values, 255)], axis=1)
    img[:] = cv2.GaussianBlur(img, (0, 0), 0.8)

    pts = poly_param(
        lambda a: np.cos(a) / (1.0 + np.sin(a) ** 2),
        lambda a: np.sin(a) * np.cos(a) / (1.0 + np.sin(a) ** 2),
        0,
        2 * math.pi,
        1400,
        W * 0.5,
        H * 0.48,
        312,
        312,
    )
    draw_neon_polyline(img, pts, hsv_to_bgr(114 + 18 * math.sin(t), 230, 250), False, 2)
    for i in range(5):
        cv2.circle(img, (int(W * 0.18 + i * 126), int(H * 0.84)), 18 + int(8 * math.sin(t * 2 + i)), (210, 230, 235), 1, cv2.LINE_AA)
    draw_title(img, "ESCENA 4: LEMNISCATA + PARTICULAS", "Campo procedural de puntos y blur como post local")


def scene_spiral_final(img, t, state):
    background_hsv_gradient(img, t, 170, 130, 26)
    draw_grid(img, t * 0.8, (58, 64, 94))
    theta_max = 8.5 * math.pi
    pts = poly_param(
        lambda th: np.exp(0.075 * th) * np.cos(th + t * 0.35),
        lambda th: np.exp(0.075 * th) * np.sin(th + t * 0.35),
        0,
        theta_max,
        1600,
        W * 0.5,
        H * 0.47,
        18,
        18,
    )
    draw_neon_polyline(img, pts, hsv_to_bgr(162 + 12 * math.sin(t), 210, 252), False, 2)

    # Segunda capa paramétrica: curva mariposa, usada como cierre visual.
    butterfly = poly_param(
        lambda a: np.sin(a) * (np.exp(np.cos(a)) - 2 * np.cos(4 * a) - np.sin(a / 12) ** 5),
        lambda a: -np.cos(a) * (np.exp(np.cos(a)) - 2 * np.cos(4 * a) - np.sin(a / 12) ** 5),
        0,
        12 * math.pi,
        2200,
        W * 0.5,
        H * 0.45,
        58,
        58,
    )
    overlay = np.zeros_like(img)
    draw_neon_polyline(overlay, butterfly, hsv_to_bgr(8 + 12 * math.sin(t * 0.5), 230, 248), False, 1)
    cv2.addWeighted(img, 0.78, overlay, 0.88, 0.0, img)

    crystal = regular_polygon(W * 0.5, H * 0.47, 56 + 8 * math.sin(t * 1.8), 6, t * 0.8)
    cv2.fillPoly(img, [crystal], (208, 230, 236), cv2.LINE_AA)
    cv2.polylines(img, [crystal], True, (45, 72, 90), 2, cv2.LINE_AA)
    cv2.putText(img, "FIN", (360, 500), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (238, 238, 238), 2, cv2.LINE_AA)
    draw_title(img, "ESCENA 5: ESPIRAL LOGARITMICA", "Final con composicion addWeighted y curva mariposa")


SCENES = [
    ("Intro / Superelipse", scene_intro),
    ("Lissajous", scene_lissajous),
    ("Rosa polar", scene_rose),
    ("Hipotrocoide + transformaciones", scene_spirograph),
    ("Lemniscata + particulas", scene_lemniscate_particles),
    ("Espiral final", scene_spiral_final),
]


def render_scene(scene_id, img, t, state):
    SCENES[scene_id][1](img, t, state)


def post_vignette(img, state):
    out = img.astype(np.float32) * state["vignette"][:, :, None]
    return np.clip(out, 0, 255).astype(np.uint8)


def post_scanlines(img, strength=0.13):
    out = img.astype(np.float32)
    y = np.arange(H, dtype=np.float32)
    m = 1.0 - strength * (0.5 + 0.5 * np.sin(2.0 * np.pi * y / 3.0))
    out *= m[:, None, None]
    return np.clip(out, 0, 255).astype(np.uint8)


def post_posterize(img, q=16):
    q = max(1, int(q))
    return ((img // q) * q).astype(np.uint8)


def post_radial_bloom(img, state):
    mask = state["radial"][:, :, None]
    blur = cv2.GaussianBlur(img, (0, 0), 7.5)
    return cv2.addWeighted(img, 0.88, (blur.astype(np.float32) * mask).astype(np.uint8), 0.32, 0.0)


def timeline(t, state, duration=DURATION):
    scene_len = duration / SCENE_COUNT
    scene_id = min(SCENE_COUNT - 1, int(t // scene_len))
    local_t = t - scene_id * scene_len
    buf_a = np.zeros((H, W, 3), np.uint8)
    buf_b = np.zeros((H, W, 3), np.uint8)
    render_scene(scene_id, buf_a, local_t, state)
    frame = buf_a

    if scene_id < SCENE_COUNT - 1 and local_t >= scene_len - TRANSITION:
        render_scene(scene_id + 1, buf_b, 0.0, state)
        a = smoothstep(scene_len - TRANSITION, scene_len, local_t)
        frame = cv2.addWeighted(buf_a, 1.0 - a, buf_b, a, 0.0)
        flash = smoothstep(scene_len - 0.28, scene_len, local_t)
        if flash > 0.0:
            frame = cv2.addWeighted(frame, 1.0, np.full_like(frame, 255), 0.10 * flash, 0.0)

    fade_in = smoothstep(0.0, 1.4, t)
    fade_out = 1.0 - smoothstep(duration - 1.6, duration, t)
    frame = (frame.astype(np.float32) * (fade_in * fade_out)).astype(np.uint8)
    frame = post_radial_bloom(frame, state)
    frame = post_vignette(frame, state)
    frame = post_scanlines(frame, 0.12)
    frame = post_posterize(frame, 12)
    return frame


def save_masks(output_dir, state):
    vignette = np.round(state["vignette"] * 255).astype(np.uint8)
    radial = np.round(state["radial"] * 255).astype(np.uint8)
    cv2.imwrite(str(output_dir / "mask_vignette.png"), vignette)
    cv2.imwrite(str(output_dir / "mask_radial_bloom.png"), radial)


def save_captures(output_dir, duration):
    output_dir.mkdir(parents=True, exist_ok=True)
    state = make_state()
    scene_len = duration / SCENE_COUNT
    for i, (name, _) in enumerate(SCENES):
        t = i * scene_len + scene_len * 0.52
        frame = timeline(t, state, duration)
        safe_name = name.lower().replace(" ", "_").replace("/", "-").replace("+", "mas")
        cv2.imwrite(str(output_dir / f"scene_{i:02d}_{safe_name}.png"), frame)
    save_masks(output_dir, state)


def export_video(path, duration):
    path.parent.mkdir(parents=True, exist_ok=True)
    state = make_state()
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, FPS, (W, H))
    if not writer.isOpened():
        raise RuntimeError("No se pudo abrir VideoWriter para exportar MP4.")

    total_frames = int(duration * FPS)
    start = time.perf_counter()
    for frame_id in range(total_frames):
        frame = timeline(frame_id / FPS, state, duration)
        writer.write(frame)
        if frame_id % FPS == 0:
            second = frame_id // FPS
            print(f"Exportando {second:02d}s / {int(duration):02d}s", end="\r")
    writer.release()
    print(f"\nVideo exportado en {time.perf_counter() - start:.2f}s: {path}")


def preview(duration):
    state = make_state()
    total_frames = int(duration * FPS)
    start = time.perf_counter()
    for frame_id in range(total_frames):
        t = frame_id / FPS
        frame = timeline(t, state, duration)
        cv2.imshow("Proyecto Final: Demo Procedural con OpenCV", frame)
        elapsed = time.perf_counter() - start
        wait = max(1, int(1000 / FPS - (elapsed - t) * 1000))
        if cv2.waitKey(wait) & 0xFF == 27:
            break
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Proyecto Final: Demo Procedural con OpenCV.")
    parser.add_argument("--preview", action="store_true", help="Muestra la demo en una ventana.")
    parser.add_argument("--export", action="store_true", help="Exporta renders/demo_procedural.mp4.")
    parser.add_argument("--captures", action="store_true", help="Guarda una captura por escena y mascaras.")
    parser.add_argument("--duration", type=float, default=DURATION, help="Duracion en segundos, entre 30 y 60.")
    parser.add_argument("--out", type=Path, default=Path("renders/demo_procedural.mp4"), help="Ruta del video MP4.")
    parser.add_argument("--renders", type=Path, default=Path("renders"), help="Carpeta de capturas.")
    args = parser.parse_args()

    duration = float(np.clip(args.duration, 30.0, 60.0))
    if args.captures:
        save_captures(args.renders, duration)
    if args.export:
        export_video(args.out, duration)
    if args.preview or (not args.export and not args.captures):
        preview(duration)


if __name__ == "__main__":
    main()
