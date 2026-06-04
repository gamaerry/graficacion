import math
import os
import sys
import threading
import time

import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluLookAt, gluPerspective

try:
    import cv2
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
except ImportError:
    cv2 = None
    mp = None
    python = None
    vision = None


SVG_W, SVG_H = 2213.0, 2135.0
SCALE = 70.0
MODEL_PATH = os.environ.get("HAND_LANDMARKER_MODEL", "hand_landmarker.task")

keys = {}
cenital_view = False
orange_mode = False
EYE_HEIGHT = 0.18
BUILDING_HEIGHT_SCALE = 0.65
COLLISION_RADIUS = 0.08
MOUSE_SENSITIVITY = 0.12
DOUBLE_TAP_SECONDS = 0.32
FALL_GRAVITY = 4.8
TERMINAL_FALL_SPEED = 5.5
ROOF_OVERHANG = 0.08
ROOF_THICKNESS = 0.13
LABEL_HEIGHT = 0.16
LABEL_DEPTH_OFFSET = 0.004
LABEL_MARGIN = 0.025
LABEL_STROKE_WIDTH = 0.18
GESTURE_CAMERA_WIDTH = 320
GESTURE_CAMERA_HEIGHT = 240
GESTURE_TARGET_FPS = 20.0
GESTURE_DEADZONE = 0.12
GESTURE_TURN_MULTIPLIER = 1.15
GESTURE_WALK_MULTIPLIER = 0.45
GESTURE_PAN_MULTIPLIER = 2.4
GESTURE_DEBUG_WINDOW = "Debug gestos ITM"

HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
)

camera_pos = [-1.5, EYE_HEIGHT, 5.4]
camera_yaw = -88.0
camera_pitch = -2.0
camera_speed = 1.45
fly_speed = 2.4
turn_speed = 95.0
mouse_look = True
first_mouse = True
last_mouse_x = 0.0
last_mouse_y = 0.0
walk_phase = 0.0
walk_bob_amount = 0.0
flight_mode = False
gesture_mode = False
gesture_controller = None
last_space_press = -10.0
roof_descent_mode = False
falling_mode = False
ground_override_mode = False
fall_velocity = 0.0

GRAY_SURFACE = (0.82, 0.82, 0.82)
EDGE_COLOR = (0.09, 0.09, 0.09)
CAMPUS_LAWN_COLOR = (0.77, 0.88, 0.70)
LAWN_COLOR = (0.77, 0.88, 0.70)
FIELD_COLOR = (0.62, 0.80, 0.22)
TRACK_COLOR = (0.73, 0.56, 0.29)
GROUND_COLOR = (0.86, 0.90, 0.84)
SKY_COLOR = (0.64, 0.78, 0.92)
FENCE_BASE_COLOR = (0.34, 0.36, 0.34)
GREEN_Y = 0.01
BASE_GREEN_Y = 0.005
GRAY_Y = 0.018
EDGE_Y = 0.07
SPORT_Y = 0.022
FENCE_BASE_Y = 0.055
FENCE_BASE_HEIGHT = 0.32
FENCE_BASE_WIDTH = 0.20
FENCE_COLLISION_RADIUS = 0.18
FENCE_SLIDE_EPSILON = 0.015
RIGHT_SECTION_DX = 120


def shift_points(points, dx, dy=0):
    return [(x + dx, y + dy) for x, y in points]


CAMPUS_BASE_AREAS = [
    # Area 1: Bloque occidental (trapezoide refinado)
    [(140, 180), (580, 180), (220, 1020), (140, 1020)],
    # Area 2: Bloque central y oriental (polígono principal siguiendo vialidad)
    [(1050, 260), (1850, 320), (2000, 850), (1850, 1450), (1650, 1950), (1150, 1750), (250, 1300), (750, 650)],
    # Area 3: Bloque sur-oriental (triángulo refinado)
    shift_points([(1750, 1800), (2200, 1950), (2020, 2130), (1700, 2040)], RIGHT_SECTION_DX),
]

CAMPUS_FENCE_AREAS = [
    # Area 1 con el triangulo oriental incluido.
    [(140, 180), (580, 180), (781, 257), (220, 1020), (140, 1020)],
    # Area 2 ajustada para abrazar el sur del campus sin invadir la carretera oriental.
    [(1050, 260), (1850, 320), (2055, 820), (1880, 1460), (1630, 1985), (1140, 1815), (720, 1625), (230, 1375), (750, 650)],
    # Area 3 con el triangulo norte incluido.
    shift_points([(1917, 1585), (2200, 1950), (2020, 2130), (1700, 2040), (1750, 1800)], RIGHT_SECTION_DX),
]

CAMPUS_FILL_AREAS = [
    CAMPUS_FENCE_AREAS[1],
]

BASE_GREEN_COLOR = (0.792, 0.894, 0.725)

GREEN_AREAS = [
    [(551, 182), (721, 289), (191, 1011), (144, 1011), (138, 572), (143, 304), (348, 190)],
    [(1050, 267), (1399, 289), (1400, 340), (1048, 269), (999, 330), (760, 630), (992, 638)],
    [(1011, 921), (1991, 854), (1991, 883), (1982, 959), (1971, 1026), (1940, 1146), (1905, 1267), (1826, 1515), (999, 1513), (1006, 1131)],
    [(997, 1709), (1301, 1838), (1649, 1984), (1841, 1464), (994, 1466)],
    [(387, 1315), (261, 1312), (317, 1217), (372, 1122), (469, 955), (492, 954), (489, 1118), (393, 1116)],
    [(632, 1340), (257, 1331), (244, 1337), (238, 1352), (248, 1381), (397, 1450), (584, 1538), (591, 1432)],
    [(996, 1225), (713, 1220), (711, 1327), (994, 1332)],
    shift_points([(1760, 1800), (2208, 1945), (2015, 2132), (1708, 2042)], RIGHT_SECTION_DX),
    [(1015, 1530), (1242, 1534), (1241, 1560), (1014, 1556)],
    # Nuevos triángulos de relleno (Modificación quirúrgica solicitada)
    [(580, 180), (781, 257), (220, 1020)],
    shift_points([(1750, 1800), (1917, 1585), (2200, 1950)], RIGHT_SECTION_DX),
]


ROADS = [
    [(1004, 107), (1007, 85), (246, 1109), (251, 1116)],
    [(6, 1402), (1432, 2014), (1436, 2020), (1427, 2020), (7, 1414)],
    [(715, 1439), (1009, 1445), (1007, 1557), (943, 1601), (1009, 1601), (1009, 1623), (1244, 1627), (1240, 1734), (1444, 1752), (1441, 1897), (1233, 1813), (591, 1533), (593, 1481), (717, 1483)],
    [(1037, 1451), (1207, 1454), (1210, 1327), (1224, 1326), (1222, 1455), (1708, 1467), (1704, 1771), (1628, 1770), (1625, 1975), (1607, 1967), (1608, 1722), (1683, 1723), (1685, 1486), (1037, 1468)],
]


CONCRETE_AREAS = [
    [(391, 1113), (1007, 1124), (1001, 1455), (385, 1444)],
    [(715, 1439), (862, 1442), (1009, 1445), (1007, 1557), (943, 1601), (1009, 1601), (1009, 1623), (1244, 1627), (1240, 1734), (1444, 1752), (1441, 1897), (1233, 1813), (1001, 1715), (770, 1615), (591, 1533), (593, 1481), (717, 1483)],
    [(1037, 1451), (1207, 1454), (1210, 1327), (1224, 1326), (1222, 1455), (1708, 1467), (1704, 1771), (1628, 1770), (1625, 1975), (1607, 1967), (1608, 1722), (1683, 1723), (1685, 1486), (1037, 1468)],
    [(243, 220), (604, 227), (713, 295), (697, 321), (630, 280), (564, 279), (561, 295), (432, 293), (432, 278), (355, 253), (254, 252), (230, 284), (229, 321), (253, 321), (249, 462), (247, 633), (239, 645), (228, 652), (214, 654), (202, 650), (191, 642), (185, 630), (190, 320), (202, 274)],
    [(1069, 471), (954, 471), (935, 449), (919, 434), (985, 352), (1051, 270), (1225, 280), (1398, 289), (1399, 322), (1449, 324), (1450, 290), (1469, 294), (1540, 321), (1548, 339), (1546, 462), (1531, 479), (1514, 488), (1509, 502), (1509, 544), (1498, 561), (1483, 567), (1423, 567), (1418, 825), (1344, 825), (1344, 957), (1322, 955), (1323, 848), (1324, 741), (1290, 739), (1295, 397), (1183, 395), (1072, 393)],
    [(759, 843), (1208, 851), (1206, 976), (757, 968)],
    [(487, 961), (698, 965), (695, 1119), (484, 1115)],
    [(944, 1342), (1033, 1344), (1030, 1546), (940, 1544)],
    [(1357, 1298), (1441, 1300), (1439, 1432), (1356, 1430)],
    [(1120, 285), (1468, 292), (1542, 322), (1548, 462), (1532, 480), (1513, 490), (1509, 560), (1485, 568), (1424, 567), (1420, 690), (1350, 690), (1350, 824), (1325, 823), (1324, 740), (1290, 739), (1295, 397), (1184, 395), (1122, 392)],
    [(1198, 736), (1368, 739), (1365, 958), (1192, 955)],
    [(1351, 998), (1512, 1002), (1509, 1092), (1350, 1090)],
    [(1223, 1111), (1335, 1113), (1334, 1210), (1223, 1207)],
    [(1001, 1218), (1350, 1228), (1350, 1240), (1001, 1233)],
    [(1097, 1223), (1350, 1228), (1350, 1240), (1097, 1235)],
    [(1000, 1320), (1107, 1322), (1107, 1329), (1000, 1327)],
    [(1259, 1255), (1334, 1257), (1335, 1233), (1259, 1232)],
    [(1246, 1291), (1334, 1293), (1333, 1301), (1246, 1299)],
    [(1249, 1353), (1283, 1353), (1283, 1402), (1248, 1401)],
    [(1539, 1335), (1557, 1336), (1554, 1464), (1537, 1463)],
    [(714, 1220), (994, 1225), (994, 1332), (711, 1327)],
    [(255, 1308), (652, 1317), (651, 1338), (254, 1331)],
    [(386, 1373), (651, 1378), (651, 1389), (386, 1385)],
    [(588, 1469), (706, 1471), (705, 1487), (588, 1485)],
    [(677, 1761), (739, 1772), (733, 1785), (665, 1756)],
    [(739, 1620), (801, 1631), (795, 1644), (744, 1607)],
    [(1087, 630), (1283, 634), (1283, 641), (1087, 637)],
    [(1039, 637), (1168, 639), (1168, 652), (1039, 650)],
    [(992, 849), (1196, 853), (1196, 871), (992, 868)],
    [(1006, 1064), (1193, 1067), (1193, 1082), (1005, 1078)],
    [(1097, 1223), (1350, 1228), (1350, 1240), (1097, 1235)],
    shift_points([(1978, 1952), (1988, 1927), (1936, 1910), (1927, 1935)], RIGHT_SECTION_DX),
    shift_points([(1868, 1959), (1912, 1977), (1895, 2014), (1851, 1996)], RIGHT_SECTION_DX),
    [(1409, 1460), (1438, 1461), (1438, 1431), (1410, 1431)],
]


RECTANGULAR_GRAY_AREAS = [
    [(170, 250), (620, 258), (620, 305), (170, 297)],
    [(170, 320), (530, 327), (528, 390), (168, 383)],
    [(170, 420), (535, 427), (533, 485), (168, 478)],
    [(170, 525), (575, 532), (573, 620), (168, 613)],
    [(170, 675), (520, 682), (518, 775), (168, 768)],
    [(1020, 300), (1475, 310), (1530, 520), (980, 510)],
    [(980, 520), (1545, 532), (1538, 895), (970, 884)],
    [(760, 870), (1210, 878), (1206, 980), (755, 972)],
    [(490, 955), (700, 960), (695, 1120), (485, 1115)],
    [(385, 1115), (1005, 1126), (1000, 1330), (380, 1320)],
    [(385, 1330), (1005, 1340), (1000, 1456), (382, 1446)],
    [(715, 1440), (1010, 1446), (1006, 1625), (708, 1618)],
    [(1005, 1460), (1390, 1470), (1384, 1630), (1000, 1622)],
    [(1240, 1625), (1445, 1640), (1440, 1898), (1235, 1815)],
    [(1550, 1245), (1825, 1254), (1820, 1460), (1545, 1452)],
    [(1038, 1452), (1708, 1468), (1704, 1500), (1037, 1484)],
    [(1608, 1722), (1683, 1723), (1680, 1980), (1605, 1968)],
    shift_points([(1796, 1836), (1995, 1831), (1964, 1905), (1827, 1888)], RIGHT_SECTION_DX),
    shift_points([(1868, 1959), (1912, 1977), (1895, 2014), (1851, 1996)], RIGHT_SECTION_DX),
    shift_points([(1880, 1875), (1978, 1910), (1942, 1990), (1845, 1954)], RIGHT_SECTION_DX),
]


WALKWAYS = [
    [(466, 291), (479, 291), (473, 621), (460, 621)],
    [(1028, 523), (1041, 523), (1036, 798), (1023, 797)],
    [(1028, 536), (1297, 541), (1297, 558), (1027, 553)],
    [(760, 631), (1286, 641), (1286, 656), (740, 648)],
    [(1195, 955), (1500, 961), (1499, 976), (1195, 970)],
    [(700, 918), (717, 918), (713, 1099), (697, 1098)],
    [(559, 1134), (573, 1134), (570, 1265), (557, 1265)],
    [(697, 1095), (1006, 1101), (1005, 1119), (697, 1113)],
    [(714, 1220), (863, 1223), (863, 1236), (713, 1233)],
    [(989, 1119), (1004, 1120), (1000, 1327), (985, 1327)],
    [(944, 1332), (1207, 1336), (1207, 1348), (944, 1343)],
    [(1555, 1445), (1751, 1448), (1751, 1468), (1554, 1464)],
    shift_points([(1827, 1761), (1995, 1831), (1964, 1905), (1796, 1836)], RIGHT_SECTION_DX),
    [(738, 1589), (750, 1594), (677, 1761), (665, 1756)],
]


BUILDINGS = [
    ("3a", shift_points([(1800, 1836), (1888, 1872), (1853, 1949), (1764, 1913)], RIGHT_SECTION_DX), 1.1),
    ("3b", shift_points([(1948, 1738), (2019, 1767), (1995, 1823), (1924, 1794)], RIGHT_SECTION_DX), 1.0),
    ("aa", [(1260, 1254), (1335, 1255), (1334, 1289), (1259, 1288)], 1.0),
    ("y", [(1458, 1298), (1538, 1300), (1537, 1382), (1456, 1380)], 1.7),
    ("2j", [(273, 320), (367, 322), (367, 359), (272, 357)], 1.0),
    ("2f", [(518, 366), (604, 368), (603, 401), (517, 399)], 1.0),
    ("2h", [(269, 411), (365, 413), (365, 452), (268, 450)], 1.0),
    ("2d", [(314, 518), (435, 520), (434, 568), (314, 565)], 1.1),
    ("2c", [(309, 596), (359, 597), (358, 618), (309, 617)], 0.8),
    ("2b", [(372, 597), (412, 598), (411, 646), (371, 645)], 0.8),
    ("2a", [(182, 660), (335, 663), (334, 706), (280, 705), (279, 749), (334, 750), (333, 794), (180, 791), (181, 747), (235, 748), (236, 704), (181, 703)], 1.1),
    ("f", [(998, 798), (1137, 801), (1136, 836), (997, 834)], 1.0),
    ("o", [(855, 1124), (988, 1126), (988, 1158), (854, 1156)], 1.0),
    ("ene", [(726, 1119), (781, 1120), (780, 1181), (725, 1180)], 1.0),
    ("p", [(790, 1179), (852, 1181), (851, 1215), (789, 1214)], 1.0),
    ("r", [(1012, 1241), (1067, 1242), (1066, 1314), (1011, 1313)], 1.0),
    ("v", [(1115, 1245), (1141, 1245), (1140, 1328), (1114, 1328)], 0.75),
    ("n", [(568, 1260), (570, 1133), (655, 1135), (653, 1262)], 1.2),
    ("m", [(496, 1258), (412, 1257), (415, 1130), (498, 1132)], 1.2),
    ("u", [(747, 1341), (790, 1342), (790, 1365), (912, 1360), (944, 1357), (942, 1424), (940, 1512), (908, 1511), (908, 1506), (786, 1490), (786, 1515), (743, 1514)], 1.4),
    ("s1", [(546, 1343), (574, 1343), (573, 1372), (545, 1372)], 0.7),
    ("j", [(803, 888), (896, 889), (895, 930), (829, 929), (829, 938), (802, 937)], 1.1),
    ("c", [(1170, 497), (1285, 500), (1284, 533), (1169, 531)], 1.1),
    ("h", [(1515, 664), (1554, 665), (1549, 980), (1509, 979)], 1.6),
    ("q", [(1395, 1151), (1539, 1154), (1538, 1188), (1395, 1186)], 1.1),
    ("ab", [(1230, 1401), (1302, 1402), (1302, 1436), (1229, 1435), (1229, 1423)], 1.0),
    ("x", [(1106, 1367), (1184, 1368), (1183, 1403), (1105, 1402)], 1.0),
    ("w", [(1151, 1240), (1176, 1241), (1175, 1287), (1150, 1287)], 0.75),
    ("ac", [(1134, 1497), (1206, 1498), (1206, 1530), (1133, 1528)], 0.75),
    ("ad", [(1133, 1573), (1201, 1574), (1200, 1607), (1133, 1606)], 0.75),
    ("i", [(1016, 874), (1137, 876), (1134, 993), (1014, 990)], 0.75),
    ("s", [(444, 1267), (472, 1268), (472, 1292), (599, 1294), (599, 1269), (444, 1267)], 0.9),
    ("d", [(1096, 581), (1259, 584), (1258, 623), (1095, 620)], 1.0),
    ("z", [(1193, 1252), (1229, 1253), (1228, 1311), (1246, 1312), (1245, 1338), (1190, 1337), (1191, 1311)], 0.75),
    ("s2", [(363, 1362), (386, 1362), (385, 1394), (362, 1394)], 0.7),
    ("ch", [(1090, 395), (1253, 398), (1252, 464), (1089, 461)], 1.4),
    ("a", [(850, 533), (965, 535), (964, 611), (934, 611), (933, 645), (963, 646), (962, 728), (846, 726), (848, 644), (877, 644), (877, 609), (848, 609)], 1.7),
    ("2k", [(160, 219), (204, 220), (203, 255), (160, 254)], 0.8),
    ("l", [(506, 988), (656, 990), (656, 982), (680, 982), (680, 991), (689, 991), (688, 1016), (506, 1013)], 1.0),
    ("ae", [(1640, 1249), (1637, 1427), (1570, 1426), (1574, 1248)], 1.3),
    ("af", [(1667, 1272), (1826, 1275), (1823, 1440), (1664, 1437)], 1.5),
    ("e", [(1059, 698), (1194, 700), (1193, 733), (1059, 730)], 1.0),
    ("k", [(967, 1024), (978, 1024), (978, 1011), (999, 1011), (998, 1025), (1157, 1028), (1157, 1051), (966, 1047)], 1.0),
    ("g", [(1238, 739), (1318, 741), (1315, 895), (1235, 893)], 1.5),
    ("s3", [(1335, 750), (1366, 751), (1365, 785), (1334, 784)], 0.7),
    ("ll", [(878, 1202), (975, 1204), (973, 1288), (876, 1286)], 1.0),
    ("ag", [(1547, 408), (1546, 570), (1481, 570), (1482, 407)], 1.3),
    ("t", [(592, 1379), (699, 1381), (698, 1461), (591, 1459)], 1.2),
    ("2g", [(419, 342), (455, 343), (452, 476), (416, 475)], 1.2),
    ("2e", [(507, 501), (536, 521), (525, 537), (496, 518)], 0.9),
    ("b", [(1002, 500), (1085, 501), (1085, 535), (1002, 533)], 1.0),
    ("ah", [(1259, 1519), (1356, 1521), (1354, 1605), (1258, 1603)], 1.5),
]


SPORTS_FIELDS = [
    ("cancha", [(1660, 630), (1885, 635), (1878, 1022), (1653, 1018)]),
    ("cancha_norte", [(1714, 631), (1835, 634), (1834, 695), (1713, 693)]),
    ("cancha_sur", [(1707, 1019), (1828, 1021), (1829, 957), (1708, 955)]),
]


def clamp(value, low, high):
    return max(low, min(high, value))


def empty_gesture_command():
    return {
        "gesture": "none",
        "steer_x": 0.0,
        "steer_y": 0.0,
        "pan_x": 0.0,
        "pan_y": 0.0,
        "seen_at": 0.0,
    }


def landmark_distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def finger_extended(landmarks, tip_idx, pip_idx):
    wrist = landmarks[0]
    return landmark_distance(wrist, landmarks[tip_idx]) > landmark_distance(wrist, landmarks[pip_idx]) * 1.08


def handedness_label(handedness):
    if not handedness:
        return ""
    try:
        first = handedness[0]
    except (TypeError, IndexError):
        first = handedness
    return getattr(first, "category_name", "")


def palm_facing_camera(landmarks, handedness):
    wrist = landmarks[0]
    index_mcp = landmarks[5]
    pinky_mcp = landmarks[17]
    cross_z = (
        (index_mcp.x - wrist.x) * (pinky_mcp.y - wrist.y)
        - (index_mcp.y - wrist.y) * (pinky_mcp.x - wrist.x)
    )
    detected_label = handedness_label(handedness)
    orientation = cross_z
    return orientation >= 0.0, orientation, f"Right fijo/{detected_label}"


def classify_hand_gesture(landmarks, handedness=None):
    wrist = landmarks[0]
    index_tip = landmarks[8]
    palm_x = (landmarks[0].x + landmarks[5].x + landmarks[9].x + landmarks[13].x + landmarks[17].x) / 5.0
    palm_y = (landmarks[0].y + landmarks[5].y + landmarks[9].y + landmarks[13].y + landmarks[17].y) / 5.0

    index_extended = finger_extended(landmarks, 8, 6)
    middle_extended = finger_extended(landmarks, 12, 10)
    ring_extended = finger_extended(landmarks, 16, 14)
    pinky_extended = finger_extended(landmarks, 20, 18)
    thumb_up = landmarks[4].y < landmarks[3].y - 0.035
    thumb_open = landmark_distance(landmarks[4], landmarks[9]) > landmark_distance(landmarks[2], landmarks[9]) * 1.10

    extended_count = sum([index_extended, middle_extended, ring_extended, pinky_extended])
    is_palm_facing_camera, palm_orientation, hand_label = palm_facing_camera(landmarks, handedness)
    index_only = index_extended and not middle_extended and not ring_extended and not pinky_extended
    peace_sign = index_extended and middle_extended and not ring_extended and not pinky_extended
    command = empty_gesture_command()
    command["pan_x"] = clamp((palm_x - 0.5) / 0.35, -1.0, 1.0)
    command["pan_y"] = clamp((palm_y - 0.5) / 0.35, -1.0, 1.0)
    command["steer_x"] = clamp((index_tip.x - wrist.x) / 0.28, -1.0, 1.0)
    command["steer_y"] = clamp((wrist.y - index_tip.y) / 0.28, -1.0, 1.0)
    command["seen_at"] = time.monotonic()
    command["debug"] = {
        "index": index_extended,
        "middle": middle_extended,
        "ring": ring_extended,
        "pinky": pinky_extended,
        "thumb_up": thumb_up,
        "thumb_open": thumb_open,
        "extended_count": extended_count,
        "palm_facing_camera": is_palm_facing_camera,
        "palm_orientation": palm_orientation,
        "hand_label": hand_label,
        "peace_sign": peace_sign,
    }

    if peace_sign:
        command["gesture"] = "peace_sign"
    elif index_only:
        command["gesture"] = "index_point"
    elif extended_count == 0:
        command["gesture"] = "fist"
    elif extended_count >= 4:
        if is_palm_facing_camera:
            command["gesture"] = "open_palm"
        else:
            command["gesture"] = "open_palm_reversed"

    return command


def draw_debug_hand(frame, landmarks, command):
    height, width, _ = frame.shape
    points = []
    for landmark in landmarks:
        x = int(landmark.x * width)
        y = int(landmark.y * height)
        points.append((x, y))
        cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

    for start_idx, end_idx in HAND_CONNECTIONS:
        cv2.line(frame, points[start_idx], points[end_idx], (255, 200, 0), 1)

    wrist = points[0]
    index_tip = points[8]
    cv2.arrowedLine(frame, wrist, index_tip, (0, 0, 255), 2, tipLength=0.25)

    debug = command.get("debug", {})
    lines = [
        f"gesto: {command.get('gesture', 'none')}",
        f"steer: {command.get('steer_x', 0.0):+.2f}, {command.get('steer_y', 0.0):+.2f}",
        f"pan: {command.get('pan_x', 0.0):+.2f}, {command.get('pan_y', 0.0):+.2f}",
        "dedos: "
        f"I={int(debug.get('index', False))} "
        f"M={int(debug.get('middle', False))} "
        f"A={int(debug.get('ring', False))} "
        f"P={int(debug.get('pinky', False))}",
        f"pulgar: up={int(debug.get('thumb_up', False))} open={int(debug.get('thumb_open', False))}",
        f"palma_cam: {int(debug.get('palm_facing_camera', False))} "
        f"ori={debug.get('palm_orientation', 0.0):+.3f} mano={debug.get('hand_label', '')}",
        f"paz: {int(debug.get('peace_sign', False))}",
        "q: cerrar debug / G: apagar gestos",
    ]
    for i, text in enumerate(lines):
        y = 20 + i * 18
        cv2.putText(frame, text, (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(frame, text, (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)


def draw_debug_no_hand(frame):
    text = "Sin mano detectada"
    cv2.putText(frame, text, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(frame, text, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)


class GestureController:
    def __init__(self):
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.command = empty_gesture_command()
        self.error = None

    def start(self):
        if self.running:
            return True
        if cv2 is None or mp is None or python is None or vision is None:
            self.error = "Instala opencv-python y mediapipe para usar gestos."
            return False
        if not os.path.exists(MODEL_PATH):
            self.error = f"No se encontro el modelo '{MODEL_PATH}'."
            return False

        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        if not self.running:
            return
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=1.0)
        self.thread = None
        with self.lock:
            self.command = empty_gesture_command()

    def snapshot(self):
        with self.lock:
            return dict(self.command)

    def _publish(self, command):
        with self.lock:
            self.command = command

    def _run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, GESTURE_CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, GESTURE_CAMERA_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, GESTURE_TARGET_FPS)

        if not cap.isOpened():
            self.error = "No se pudo abrir la camara."
            self.running = False
            return

        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.55,
            min_hand_presence_confidence=0.55,
            min_tracking_confidence=0.55,
        )

        frame_interval = 1.0 / GESTURE_TARGET_FPS
        next_frame_time = 0.0
        start_time = time.monotonic()
        last_timestamp_ms = 0
        show_debug = True

        try:
            with vision.HandLandmarker.create_from_options(options) as landmarker:
                while self.running:
                    now = time.monotonic()
                    if now < next_frame_time:
                        time.sleep(min(0.01, next_frame_time - now))
                        continue
                    next_frame_time = now + frame_interval

                    ret, frame = cap.read()
                    if not ret:
                        self._publish(empty_gesture_command())
                        continue

                    frame = cv2.flip(frame, 1)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
                    timestamp_ms = max(last_timestamp_ms + 1, int((now - start_time) * 1000))
                    last_timestamp_ms = timestamp_ms

                    result = landmarker.detect_for_video(mp_image, timestamp_ms)
                    if result.hand_landmarks:
                        handedness = result.handedness[0] if result.handedness else None
                        command = classify_hand_gesture(result.hand_landmarks[0], handedness)
                        self._publish(command)
                        if show_debug:
                            draw_debug_hand(frame, result.hand_landmarks[0], command)
                    else:
                        self._publish(empty_gesture_command())
                        if show_debug:
                            draw_debug_no_hand(frame)

                    if show_debug:
                        cv2.imshow(GESTURE_DEBUG_WINDOW, frame)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            show_debug = False
                            cv2.destroyWindow(GESTURE_DEBUG_WINDOW)
        except Exception as exc:
            self.error = str(exc)
        finally:
            cap.release()
            try:
                cv2.destroyWindow(GESTURE_DEBUG_WINDOW)
            except cv2.error:
                pass
            self.running = False


def current_gesture_command():
    if not gesture_mode or gesture_controller is None:
        return empty_gesture_command()
    command = gesture_controller.snapshot()
    if time.monotonic() - command.get("seen_at", 0.0) > 0.35:
        return empty_gesture_command()
    return command


def is_ground_position_clear(x, z):
    return (
        not body_overlaps_building_world(x, z)
        and not is_blocked_world(x, z, EYE_HEIGHT)
        and not is_blocked_by_fence_world(x, z, EYE_HEIGHT)
    )


def nearest_clear_ground_position(x, z):
    if is_ground_position_clear(x, z):
        return x, z

    for ring in range(1, 28):
        radius = ring * 0.12
        samples = max(12, ring * 8)
        for sample in range(samples):
            angle = (math.tau * sample) / samples
            test_x = x + math.cos(angle) * radius
            test_z = z + math.sin(angle) * radius
            if is_ground_position_clear(test_x, test_z):
                return test_x, test_z

    return x, z


def place_camera_on_ground():
    global ground_override_mode, roof_descent_mode, falling_mode, fall_velocity

    camera_pos[0], camera_pos[2] = nearest_clear_ground_position(camera_pos[0], camera_pos[2])
    camera_pos[1] = EYE_HEIGHT
    ground_override_mode = False
    roof_descent_mode = False
    falling_mode = False
    fall_velocity = 0.0


def set_normal_person_mode():
    global cenital_view, flight_mode, camera_pitch, camera_yaw, first_mouse
    global falling_mode, ground_override_mode, roof_descent_mode, fall_velocity

    was_cenital = cenital_view
    if cenital_view:
        cenital_view = False
        first_mouse = True
        camera_pitch = -2.0
    if was_cenital:
        place_camera_on_ground()
    elif flight_mode:
        falling_mode = True
        fall_velocity = 0.0
        ground_override_mode = False
        roof_descent_mode = False
    else:
        roof_descent_mode = False
        if not falling_mode:
            fall_velocity = 0.0
    flight_mode = False


def apply_gesture_mode_switch(gesture_name):
    global cenital_view, flight_mode, camera_pitch, camera_yaw, first_mouse
    global falling_mode, ground_override_mode, roof_descent_mode, fall_velocity

    if gesture_name in ("index_point", "none"):
        set_normal_person_mode()
    elif gesture_name == "open_palm":
        was_cenital = cenital_view
        if cenital_view:
            cenital_view = False
            first_mouse = True
            camera_pitch = -2.0
        if not flight_mode:
            if was_cenital:
                place_camera_on_ground()
                camera_pos[1] = EYE_HEIGHT + 0.08
            else:
                camera_pos[1] = max(camera_pos[1], standing_eye_height(camera_pos[0], camera_pos[2]) + 0.08)
        flight_mode = True
        falling_mode = False
        ground_override_mode = False
        roof_descent_mode = False
        fall_velocity = 0.0
    elif gesture_name == "peace_sign":
        if not cenital_view:
            cenital_view = True
            flight_mode = False
            falling_mode = False
            ground_override_mode = False
            roof_descent_mode = False
            fall_velocity = 0.0
            camera_pos[1] = 24.0
            camera_pitch = -89.0
            camera_yaw = -90.0


def toggle_gesture_mode():
    global gesture_mode, gesture_controller
    if gesture_controller is None:
        gesture_controller = GestureController()

    if gesture_mode:
        gesture_controller.stop()
        gesture_mode = False
    else:
        gesture_mode = gesture_controller.start()


def key_callback(window, key, scancode, action, mods):
    global cenital_view, camera_pitch, camera_yaw, orange_mode, first_mouse
    global flight_mode, last_space_press, roof_descent_mode
    global falling_mode, ground_override_mode, fall_velocity
    if action == glfw.PRESS:
        keys[key] = True
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        if key == glfw.KEY_G:
            toggle_gesture_mode()
        if key == glfw.KEY_SPACE and not cenital_view:
            now = glfw.get_time()
            if now - last_space_press <= DOUBLE_TAP_SECONDS:
                flight_mode = not flight_mode
                if flight_mode:
                    roof_descent_mode = False
                    falling_mode = False
                    ground_override_mode = False
                    fall_velocity = 0.0
                    camera_pos[1] = max(camera_pos[1], standing_eye_height(camera_pos[0], camera_pos[2]) + 0.08)
                else:
                    roof_descent_mode = False
                    ground_override_mode = False
                    falling_mode = True
                    fall_velocity = 0.0
                last_space_press = -10.0
            else:
                last_space_press = now
        if key == glfw.KEY_M:
            orange_mode = not orange_mode
        if key == glfw.KEY_C:
            cenital_view = not cenital_view
            if cenital_view:
                flight_mode = False
                roof_descent_mode = False
                falling_mode = False
                ground_override_mode = False
                fall_velocity = 0.0
                camera_pos[1] = 24.0
                camera_pitch = -89.0
                camera_yaw = -90.0
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            else:
                place_camera_on_ground()
                camera_pitch = -2.0
                first_mouse = True
                if mouse_look:
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    elif action == glfw.RELEASE:
        keys[key] = False


def cursor_pos_callback(window, xpos, ypos):
    global camera_yaw, camera_pitch, first_mouse, last_mouse_x, last_mouse_y
    if cenital_view or not mouse_look:
        first_mouse = True
        return

    if first_mouse:
        last_mouse_x = xpos
        last_mouse_y = ypos
        first_mouse = False
        return

    dx = xpos - last_mouse_x
    dy = ypos - last_mouse_y
    last_mouse_x = xpos
    last_mouse_y = ypos

    camera_yaw += dx * MOUSE_SENSITIVITY
    camera_pitch -= dy * MOUSE_SENSITIVITY
    camera_pitch = max(-65.0, min(28.0, camera_pitch))


def mouse_button_callback(window, button, action, mods):
    pass


def scroll_callback(window, xoffset, yoffset):
    if not cenital_view and not flight_mode:
        return
    min_height = 6.0 if cenital_view else EYE_HEIGHT
    camera_pos[1] = max(min_height, camera_pos[1] + yoffset * fly_speed * 0.35)


def svg_to_world(point):
    x, y = point
    return ((x - SVG_W * 0.5) / SCALE, (y - SVG_H * 0.5) / SCALE)


def world_to_svg(point):
    x, z = point
    return (x * SCALE + SVG_W * 0.5, z * SCALE + SVG_H * 0.5)


def color3(color):
    glColor3f(color[0], color[1], color[2])


def shade_color(color, factor):
    return tuple(max(0.0, min(1.0, component * factor)) for component in color)


def polygon_area_2d(points):
    area = 0.0
    for i, (x1, y1) in enumerate(points):
        x2, y2 = points[(i + 1) % len(points)]
        area += x1 * y2 - x2 * y1
    return area * 0.5


def cross_2d(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def point_in_triangle(p, a, b, c):
    c1 = cross_2d(a, b, p)
    c2 = cross_2d(b, c, p)
    c3 = cross_2d(c, a, p)
    has_neg = c1 < -1e-6 or c2 < -1e-6 or c3 < -1e-6
    has_pos = c1 > 1e-6 or c2 > 1e-6 or c3 > 1e-6
    return not (has_neg and has_pos)


def triangulate_polygon(points):
    if len(points) < 3:
        return []
    if len(points) == 3:
        return [points]

    verts = list(points)
    if polygon_area_2d(verts) < 0:
        verts.reverse()

    indices = list(range(len(verts)))
    triangles = []
    guard = 0

    while len(indices) > 3 and guard < len(verts) * len(verts):
        guard += 1
        ear_found = False
        for pos, idx in enumerate(indices):
            prev_idx = indices[pos - 1]
            next_idx = indices[(pos + 1) % len(indices)]
            a, b, c = verts[prev_idx], verts[idx], verts[next_idx]

            if cross_2d(a, b, c) <= 1e-6:
                continue

            if any(
                point_in_triangle(verts[test_idx], a, b, c)
                for test_idx in indices
                if test_idx not in (prev_idx, idx, next_idx)
            ):
                continue

            triangles.append([a, b, c])
            del indices[pos]
            ear_found = True
            break

        if not ear_found:
            break

    if len(indices) == 3:
        triangles.append([verts[indices[0]], verts[indices[1]], verts[indices[2]]])

    if not triangles:
        anchor = verts[0]
        triangles = [[anchor, verts[i], verts[i + 1]] for i in range(1, len(verts) - 1)]
    return triangles


def draw_flat_polygon(points, color, y=0.01):
    color3(color)
    glBegin(GL_TRIANGLES)
    for tri in triangulate_polygon(points):
        for p in tri:
            x, z = svg_to_world(p)
            glVertex3f(x, y, z)
    glEnd()


def draw_line_loop(points, color, y=0.04, width=1.0):
    glLineWidth(width)
    color3(color)
    glBegin(GL_LINE_LOOP)
    for p in points:
        x, z = svg_to_world(p)
        glVertex3f(x, y, z)
    glEnd()
    glLineWidth(1.0)


def draw_polyline_world(points, color, y=0.04, width=1.0, closed=False):
    glLineWidth(width)
    color3(color)
    glBegin(GL_LINE_LOOP if closed else GL_LINE_STRIP)
    for x, z in points:
        glVertex3f(x, y, z)
    glEnd()
    glLineWidth(1.0)


def draw_ellipse(cx, cy, rx, ry, color, y, segments=80):
    color3(color)
    glBegin(GL_POLYGON)
    for i in range(segments):
        a = i * 2.0 * math.pi / segments
        x, z = svg_to_world((cx + math.cos(a) * rx, cy + math.sin(a) * ry))
        glVertex3f(x, y, z)
    glEnd()


def ellipse_points(cx, cy, rx, ry, segments=72):
    pts = []
    for i in range(segments):
        a = i * 2.0 * math.pi / segments
        pts.append(svg_to_world((cx + math.cos(a) * rx, cy + math.sin(a) * ry)))
    return pts


def interp_world(a, b, t):
    ax, az = a
    bx, bz = b
    return (ax * (1.0 - t) + bx * t, az * (1.0 - t) + bz * t)


def draw_field(points):
    draw_flat_polygon(points, FIELD_COLOR, SPORT_Y)
    draw_line_loop(points, (0.96, 0.96, 0.92), SPORT_Y + 0.004, 2.0)

    world = [svg_to_world(p) for p in points]
    if len(world) != 4:
        return

    a, b, c, d = world
    
    # Detectar orientación
    dist_horiz = math.dist(a, b)
    dist_vert = math.dist(a, d)
    horizontal = dist_horiz > dist_vert

    if horizontal:
        m1 = interp_world(a, b, 0.5)
        m2 = interp_world(d, c, 0.5)
    else:
        m1 = interp_world(a, d, 0.5)
        m2 = interp_world(b, c, 0.5)

    glLineWidth(1.8)
    color3((0.96, 0.96, 0.92))
    glBegin(GL_LINES)
    glVertex3f(m1[0], SPORT_Y + 0.005, m1[1])
    glVertex3f(m2[0], SPORT_Y + 0.005, m2[1])
    glEnd()

    cx = (a[0] + b[0] + c[0] + d[0]) / 4.0
    cz = (a[1] + b[1] + c[1] + d[1]) / 4.0
    circle = [(cx + math.cos(i * 2 * math.pi / 48) * 0.55, cz + math.sin(i * 2 * math.pi / 48) * 0.55) for i in range(48)]
    draw_polyline_world(circle, (0.96, 0.96, 0.92), SPORT_Y + 0.006, 1.4, True)

    for t1, t2 in [(0.08, 0.24), (0.76, 0.92)]:
        if horizontal:
            p1 = interp_world(a, b, t1)
            p2 = interp_world(d, c, t1)
            p3 = interp_world(d, c, t2)
            p4 = interp_world(a, b, t2)
            box_a = interp_world(p1, p2, 0.25)
            box_b = interp_world(p1, p2, 0.75)
            box_c = interp_world(p4, p3, 0.75)
            box_d = interp_world(p4, p3, 0.25)
        else:
            p1 = interp_world(a, d, t1)
            p2 = interp_world(b, c, t1)
            p3 = interp_world(b, c, t2)
            p4 = interp_world(a, d, t2)
            box_a = interp_world(p1, p2, 0.25)
            box_b = interp_world(p1, p2, 0.75)
            box_c = interp_world(p4, p3, 0.75)
            box_d = interp_world(p4, p3, 0.25)
        draw_polyline_world([box_a, box_b, box_c, box_d], (0.96, 0.96, 0.92), SPORT_Y + 0.006, 1.2, True)


def expand_polygon_world(points, overhang):
    cx = sum(x for x, _ in points) / len(points)
    cz = sum(z for _, z in points) / len(points)
    expanded = []
    for x, z in points:
        dx = x - cx
        dz = z - cz
        length = math.hypot(dx, dz)
        if length <= 1e-6:
            expanded.append((x, z))
        else:
            expanded.append((x + dx / length * overhang, z + dz / length * overhang))
    return expanded


STROKE_GLYPHS = {
    "0": [((0.15, 0.10), (0.85, 0.10)), ((0.85, 0.10), (0.85, 0.90)), ((0.85, 0.90), (0.15, 0.90)), ((0.15, 0.90), (0.15, 0.10))],
    "1": [((0.50, 0.10), (0.50, 0.90)), ((0.35, 0.75), (0.50, 0.90)), ((0.35, 0.10), (0.65, 0.10))],
    "2": [((0.15, 0.80), (0.35, 0.90)), ((0.35, 0.90), (0.85, 0.90)), ((0.85, 0.90), (0.85, 0.55)), ((0.85, 0.55), (0.15, 0.10)), ((0.15, 0.10), (0.85, 0.10))],
    "3": [((0.15, 0.90), (0.85, 0.90)), ((0.85, 0.90), (0.65, 0.55)), ((0.65, 0.55), (0.85, 0.10)), ((0.85, 0.10), (0.15, 0.10)), ((0.35, 0.52), (0.72, 0.52))],
    "A": [((0.15, 0.10), (0.50, 0.90)), ((0.50, 0.90), (0.85, 0.10)), ((0.30, 0.45), (0.70, 0.45))],
    "B": [((0.15, 0.10), (0.15, 0.90)), ((0.15, 0.90), (0.70, 0.90)), ((0.70, 0.90), (0.85, 0.70)), ((0.85, 0.70), (0.70, 0.52)), ((0.70, 0.52), (0.15, 0.52)), ((0.70, 0.52), (0.85, 0.30)), ((0.85, 0.30), (0.70, 0.10)), ((0.70, 0.10), (0.15, 0.10))],
    "C": [((0.85, 0.82), (0.65, 0.90)), ((0.65, 0.90), (0.20, 0.90)), ((0.20, 0.90), (0.15, 0.10)), ((0.15, 0.10), (0.65, 0.10)), ((0.65, 0.10), (0.85, 0.18))],
    "D": [((0.15, 0.10), (0.15, 0.90)), ((0.15, 0.90), (0.65, 0.90)), ((0.65, 0.90), (0.85, 0.70)), ((0.85, 0.70), (0.85, 0.30)), ((0.85, 0.30), (0.65, 0.10)), ((0.65, 0.10), (0.15, 0.10))],
    "E": [((0.85, 0.90), (0.15, 0.90)), ((0.15, 0.90), (0.15, 0.10)), ((0.15, 0.52), (0.70, 0.52)), ((0.15, 0.10), (0.85, 0.10))],
    "F": [((0.15, 0.10), (0.15, 0.90)), ((0.15, 0.90), (0.85, 0.90)), ((0.15, 0.52), (0.70, 0.52))],
    "G": [((0.85, 0.80), (0.65, 0.90)), ((0.65, 0.90), (0.20, 0.90)), ((0.20, 0.90), (0.15, 0.10)), ((0.15, 0.10), (0.80, 0.10)), ((0.80, 0.10), (0.80, 0.45)), ((0.80, 0.45), (0.50, 0.45))],
    "H": [((0.15, 0.10), (0.15, 0.90)), ((0.85, 0.10), (0.85, 0.90)), ((0.15, 0.52), (0.85, 0.52))],
    "I": [((0.20, 0.90), (0.80, 0.90)), ((0.50, 0.90), (0.50, 0.10)), ((0.20, 0.10), (0.80, 0.10))],
    "J": [((0.80, 0.90), (0.80, 0.20)), ((0.80, 0.20), (0.65, 0.10)), ((0.65, 0.10), (0.30, 0.10)), ((0.30, 0.10), (0.15, 0.25))],
    "K": [((0.15, 0.10), (0.15, 0.90)), ((0.85, 0.90), (0.15, 0.52)), ((0.15, 0.52), (0.85, 0.10))],
    "L": [((0.15, 0.90), (0.15, 0.10)), ((0.15, 0.10), (0.85, 0.10))],
    "M": [((0.12, 0.10), (0.12, 0.90)), ((0.12, 0.90), (0.50, 0.45)), ((0.50, 0.45), (0.88, 0.90)), ((0.88, 0.90), (0.88, 0.10))],
    "N": [((0.15, 0.10), (0.15, 0.90)), ((0.15, 0.90), (0.85, 0.10)), ((0.85, 0.10), (0.85, 0.90))],
    "Ñ": [((0.15, 0.10), (0.15, 0.78)), ((0.15, 0.78), (0.85, 0.10)), ((0.85, 0.10), (0.85, 0.78)), ((0.25, 0.92), (0.40, 0.98)), ((0.40, 0.98), (0.60, 0.90)), ((0.60, 0.90), (0.75, 0.96))],
    "O": [((0.20, 0.10), (0.80, 0.10)), ((0.80, 0.10), (0.85, 0.85)), ((0.85, 0.85), (0.20, 0.90)), ((0.20, 0.90), (0.15, 0.15)), ((0.15, 0.15), (0.20, 0.10))],
    "P": [((0.15, 0.10), (0.15, 0.90)), ((0.15, 0.90), (0.75, 0.90)), ((0.75, 0.90), (0.85, 0.65)), ((0.85, 0.65), (0.75, 0.52)), ((0.75, 0.52), (0.15, 0.52))],
    "Q": [((0.20, 0.10), (0.80, 0.10)), ((0.80, 0.10), (0.85, 0.85)), ((0.85, 0.85), (0.20, 0.90)), ((0.20, 0.90), (0.15, 0.15)), ((0.15, 0.15), (0.20, 0.10)), ((0.58, 0.28), (0.88, 0.02))],
    "R": [((0.15, 0.10), (0.15, 0.90)), ((0.15, 0.90), (0.75, 0.90)), ((0.75, 0.90), (0.85, 0.65)), ((0.85, 0.65), (0.75, 0.52)), ((0.75, 0.52), (0.15, 0.52)), ((0.15, 0.52), (0.85, 0.10))],
    "S": [((0.85, 0.85), (0.65, 0.90)), ((0.65, 0.90), (0.20, 0.90)), ((0.20, 0.90), (0.15, 0.55)), ((0.15, 0.55), (0.80, 0.45)), ((0.80, 0.45), (0.85, 0.10)), ((0.85, 0.10), (0.20, 0.10))],
    "T": [((0.15, 0.90), (0.85, 0.90)), ((0.50, 0.90), (0.50, 0.10))],
    "U": [((0.15, 0.90), (0.15, 0.20)), ((0.15, 0.20), (0.30, 0.10)), ((0.30, 0.10), (0.70, 0.10)), ((0.70, 0.10), (0.85, 0.20)), ((0.85, 0.20), (0.85, 0.90))],
    "V": [((0.15, 0.90), (0.50, 0.10)), ((0.50, 0.10), (0.85, 0.90))],
    "W": [((0.12, 0.90), (0.28, 0.10)), ((0.28, 0.10), (0.50, 0.48)), ((0.50, 0.48), (0.72, 0.10)), ((0.72, 0.10), (0.88, 0.90))],
    "X": [((0.15, 0.90), (0.85, 0.10)), ((0.85, 0.90), (0.15, 0.10))],
    "Y": [((0.15, 0.90), (0.50, 0.52)), ((0.85, 0.90), (0.50, 0.52)), ((0.50, 0.52), (0.50, 0.10))],
    "Z": [((0.15, 0.90), (0.85, 0.90)), ((0.85, 0.90), (0.15, 0.10)), ((0.15, 0.10), (0.85, 0.10))],
}


def building_label(name):
    if name == "ene":
        return "Ñ"
    return name.upper()


def label_point(origin, axis, normal, x, y):
    ox, oy, oz = origin
    ax, az = axis
    nx, nz = normal
    return (ox + ax * x + nx * LABEL_DEPTH_OFFSET, oy + y, oz + az * x + nz * LABEL_DEPTH_OFFSET)


def emit_label_stroke(origin, axis, normal, x1, y1, x2, y2, thickness):
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    if length <= 1e-6:
        return

    nx = -dy / length * thickness * 0.5
    ny = dx / length * thickness * 0.5
    for px, py in (
        (x1 + nx, y1 + ny),
        (x2 + nx, y2 + ny),
        (x2 - nx, y2 - ny),
        (x1 - nx, y1 - ny),
    ):
        glVertex3f(*label_point(origin, axis, normal, px, py))


def draw_stroke_label(label, origin, axis, normal, width, height):
    char_count = max(1, len(label))
    glyph_width = width / (char_count + (char_count - 1) * 0.20)
    spacing = glyph_width * 0.20
    thickness = min(glyph_width, height) * LABEL_STROKE_WIDTH
    color3((1.0, 1.0, 1.0))
    glBegin(GL_QUADS)
    cursor_x = 0.0
    for char in label:
        for (x1, y1), (x2, y2) in STROKE_GLYPHS.get(char, []):
            emit_label_stroke(
                origin,
                axis,
                normal,
                cursor_x + x1 * glyph_width,
                y1 * height,
                cursor_x + x2 * glyph_width,
                y2 * height,
                thickness,
            )
        cursor_x += glyph_width + spacing
    glEnd()


def draw_building_label(name, world, wall_height, roof_color):
    label = building_label(name)
    best_a, best_b = max(
        ((world[i], world[(i + 1) % len(world)]) for i in range(len(world))),
        key=lambda edge: (edge[0][1] + edge[1][1]) * 0.5,
    )
    ax, az = best_a
    bx, bz = best_b
    if ax > bx:
        ax, az, bx, bz = bx, bz, ax, az

    edge_dx = bx - ax
    edge_dz = bz - az
    edge_len = math.hypot(edge_dx, edge_dz)
    if edge_len <= LABEL_MARGIN * 2.0:
        return

    axis = (edge_dx / edge_len, edge_dz / edge_len)
    normal_a = (-axis[1], axis[0])
    normal_b = (axis[1], -axis[0])
    normal = normal_a if normal_a[1] >= normal_b[1] else normal_b

    label_h = min(LABEL_HEIGHT, max(0.08, wall_height - 0.08))
    label_w = max(label_h, label_h * (0.70 * len(label) + 0.35))
    label_w = min(label_w, max(0.10, edge_len - LABEL_MARGIN * 2.0))
    left_x = LABEL_MARGIN

    bottom_y = max(0.045, wall_height - label_h - 0.04)
    origin = (ax, bottom_y, az)

    color3(roof_color)
    glBegin(GL_QUADS)
    for px, py in (
        (left_x, 0.0),
        (left_x + label_w, 0.0),
        (left_x + label_w, label_h),
        (left_x, label_h),
    ):
        glVertex3f(*label_point(origin, axis, normal, px, py))
    glEnd()

    text_origin = (
        origin[0] + axis[0] * (left_x + label_w * 0.12) + normal[0] * 0.002,
        origin[1] + label_h * 0.12,
        origin[2] + axis[1] * (left_x + label_w * 0.12) + normal[1] * 0.002,
    )
    draw_stroke_label(label, text_origin, axis, normal, label_w * 0.76, label_h * 0.76)


def draw_prism(name, points, height, wall_color, roof_color):
    world = [svg_to_world(p) for p in points]
    roof = expand_polygon_world(world, ROOF_OVERHANG)
    roof_bottom = max(0.06, height - ROOF_THICKNESS)
    light_dir = (0.45, -0.55)
    
    # Paredes con sombreado simple por orientacion.
    glBegin(GL_QUADS)
    for i, (x1, z1) in enumerate(world):
        x2, z2 = world[(i + 1) % len(world)]
        edge_x = x2 - x1
        edge_z = z2 - z1
        normal_x = edge_z
        normal_z = -edge_x
        normal_len = math.hypot(normal_x, normal_z) or 1.0
        normal_x /= normal_len
        normal_z /= normal_len
        light = max(0.0, normal_x * light_dir[0] + normal_z * light_dir[1])
        color3(shade_color(wall_color, 0.66 + light * 0.30))
        glVertex3f(x1, 0.03, z1)
        glVertex3f(x2, 0.03, z2)
        glVertex3f(x2, roof_bottom, z2)
        glVertex3f(x1, roof_bottom, z1)
    glEnd()

    # Losa de techo guinda sobresaliente.
    color3(roof_color)
    glBegin(GL_POLYGON)
    for x, z in roof:
        glVertex3f(x, height, z)
    glEnd()

    # Cara inferior de la losa para que el techo se vea solido desde abajo.
    color3(shade_color(roof_color, 0.58))
    glBegin(GL_POLYGON)
    for x, z in reversed(roof):
        glVertex3f(x, roof_bottom, z)
    glEnd()

    # Faldilla vertical del techo para darle volumen hacia abajo.
    color3(shade_color(roof_color, 0.72))
    glBegin(GL_QUADS)
    for i, (x1, z1) in enumerate(roof):
        x2, z2 = roof[(i + 1) % len(roof)]
        glVertex3f(x1, roof_bottom, z1)
        glVertex3f(x2, roof_bottom, z2)
        glVertex3f(x2, height, z2)
        glVertex3f(x1, height, z1)
    glEnd()
    
    # Aristas verticales y contorno superior para leer mejor el volumen a nivel de calle.
    color3((0.12, 0.10, 0.08))
    glLineWidth(1.0)
    glBegin(GL_LINES)
    for x, z in world:
        glVertex3f(x, 0.03, z)
        glVertex3f(x, roof_bottom, z)
    glEnd()
    draw_polyline_world(roof, (0.12, 0.10, 0.08), height + 0.01, 1.0, True)
    draw_polyline_world(roof, (0.12, 0.10, 0.08), roof_bottom + 0.005, 1.0, True)
    draw_building_label(name, world, roof_bottom, roof_color)


def draw_ground(size=42):
    s = size / 2
    glBegin(GL_QUADS)
    color3(GROUND_COLOR)
    glVertex3f(-s, -0.02, s)
    glVertex3f(s, -0.02, s)
    glVertex3f(s, -0.02, -s)
    glVertex3f(-s, -0.02, -s)
    glEnd()


def draw_campus_base():
    draw_ground()
    for area in CAMPUS_FILL_AREAS:
        draw_flat_polygon(area, BASE_GREEN_COLOR, BASE_GREEN_Y)

    for area in CAMPUS_BASE_AREAS:
        draw_flat_polygon(area, BASE_GREEN_COLOR, BASE_GREEN_Y)

    for area in GREEN_AREAS:
        draw_flat_polygon(area, BASE_GREEN_COLOR, GREEN_Y)

    for area in RECTANGULAR_GRAY_AREAS:
        draw_flat_polygon(area, GRAY_SURFACE, GRAY_Y)

    for area in CONCRETE_AREAS:
        draw_flat_polygon(area, GRAY_SURFACE, GRAY_Y)

    for walkway in WALKWAYS:
        draw_flat_polygon(walkway, GRAY_SURFACE, GRAY_Y)


def draw_segment_prism(a, b, width, bottom_y, top_y, color):
    ax, az = a
    bx, bz = b
    dx = bx - ax
    dz = bz - az
    length = math.hypot(dx, dz)
    if length <= 1e-6:
        return

    nx = -dz / length
    nz = dx / length
    half_width = width * 0.5
    p1 = (ax + nx * half_width, az + nz * half_width)
    p2 = (bx + nx * half_width, bz + nz * half_width)
    p3 = (bx - nx * half_width, bz - nz * half_width)
    p4 = (ax - nx * half_width, az - nz * half_width)

    color3(color)
    glBegin(GL_QUADS)
    # Tapa superior.
    for x, z in (p1, p2, p3, p4):
        glVertex3f(x, top_y, z)

    # Lados largos.
    glVertex3f(p1[0], bottom_y, p1[1])
    glVertex3f(p2[0], bottom_y, p2[1])
    glVertex3f(p2[0], top_y, p2[1])
    glVertex3f(p1[0], top_y, p1[1])

    glVertex3f(p3[0], bottom_y, p3[1])
    glVertex3f(p4[0], bottom_y, p4[1])
    glVertex3f(p4[0], top_y, p4[1])
    glVertex3f(p3[0], top_y, p3[1])

    # Tapas de los extremos.
    glVertex3f(p2[0], bottom_y, p2[1])
    glVertex3f(p3[0], bottom_y, p3[1])
    glVertex3f(p3[0], top_y, p3[1])
    glVertex3f(p2[0], top_y, p2[1])

    glVertex3f(p4[0], bottom_y, p4[1])
    glVertex3f(p1[0], bottom_y, p1[1])
    glVertex3f(p1[0], top_y, p1[1])
    glVertex3f(p4[0], top_y, p4[1])
    glEnd()


def draw_fence_for_area(points):
    world = [svg_to_world(p) for p in points]
    base_top_y = FENCE_BASE_Y + FENCE_BASE_HEIGHT

    for i, a in enumerate(world):
        b = world[(i + 1) % len(world)]
        draw_segment_prism(a, b, FENCE_BASE_WIDTH, FENCE_BASE_Y, base_top_y, FENCE_BASE_COLOR)


def draw_campus_fences():
    for area in CAMPUS_FENCE_AREAS:
        draw_fence_for_area(area)


# Colores ITM Morelia
ITM_YELLOW = (0.95, 0.82, 0.42)
ITM_GUINDA = (0.50, 0.00, 0.00)
ITM_GRAY_WALL = (0.80, 0.80, 0.80)
ITM_GRAY_ROOF = (0.60, 0.60, 0.60)


def draw_buildings():
    global orange_mode
    for name, points, height in BUILDINGS:
        real_height = height * BUILDING_HEIGHT_SCALE
        if orange_mode:
            # Modo Naranja Original (Todo el campus, incluido edificio A)
            wall = (0.86, 0.50, 0.22)
            roof = (0.96, 0.66, 0.32)
        else:
            # Modo Institucional (Todo el campus, incluido edificio A)
            wall = ITM_YELLOW
            roof = ITM_GUINDA
            
        draw_prism(name, points, real_height, wall, roof)

        if real_height > 2.0:
            draw_window_band(points, real_height)


def draw_window_band(points, height):
    world = [svg_to_world(p) for p in points]
    color3((0.20, 0.24, 0.28))
    glLineWidth(1.4)
    glBegin(GL_LINES)
    y = 0.95
    while y < height - 0.55:
        for i in range(len(world)):
            x1, z1 = world[i]
            x2, z2 = world[(i + 1) % len(world)]
            mx1 = x1 * 0.80 + x2 * 0.20
            mz1 = z1 * 0.80 + z2 * 0.20
            mx2 = x1 * 0.20 + x2 * 0.80
            mz2 = z1 * 0.20 + z2 * 0.80
            glVertex3f(mx1, y, mz1)
            glVertex3f(mx2, y, mz2)
        y += 0.85
    glEnd()
    glLineWidth(1.0)


def draw_sports_fields():
    # Pista atletica y campo grande oriental.
    draw_ellipse(1780, 916, 215, 430, TRACK_COLOR, SPORT_Y, 96)
    draw_ellipse(1780, 916, 150, 350, FIELD_COLOR, SPORT_Y + 0.002, 96)
    draw_polyline_world(ellipse_points(1780, 916, 215, 430, 96), EDGE_COLOR, SPORT_Y + 0.006, 1.0, True)
    draw_polyline_world(ellipse_points(1780, 916, 150, 350, 96), EDGE_COLOR, SPORT_Y + 0.006, 1.0, True)
    draw_field([(1668, 664), (1890, 668), (1880, 1225), (1658, 1220)])

    # Canchas al sur del campus principal.
    draw_field([(1415, 1510), (1768, 1518), (1763, 1706), (1410, 1698)])
    draw_field([(1462, 1805), (1628, 1809), (1624, 1910), (1458, 1906)])


def is_point_in_poly(point, poly):
    x, y = point
    n = len(poly)
    inside = False
    if n < 3: return False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def draw_tree(x, z, scale=1.0):
    glPushMatrix()
    glTranslatef(x, 0.0, z)
    glScalef(scale, scale, scale)

    # Tronco cilindrico "perfecto"
    color3((0.35, 0.22, 0.10))
    segments = 16
    radius = 0.06
    height = 0.62
    glBegin(GL_QUAD_STRIP)
    for i in range(segments + 1):
        angle = i * 2.0 * math.pi / segments
        cx = math.cos(angle) * radius
        cz = math.sin(angle) * radius
        glVertex3f(cx, 0.0, cz)
        glVertex3f(cx, height, cz)
    glEnd()

    # Copas de las hojas
    color3((0.12, 0.48, 0.16))
    for dy, leaf_radius in [(0.48, 0.30), (0.70, 0.23)]:
        glBegin(GL_TRIANGLES)
        for i in range(12):
            a1 = i * 2 * math.pi / 12
            a2 = (i + 1) * 2 * math.pi / 12
            glVertex3f(0.0, dy + 0.35, 0.0)
            glVertex3f(math.cos(a1) * leaf_radius, dy, math.sin(a1) * leaf_radius)
            glVertex3f(math.cos(a2) * leaf_radius, dy, math.sin(a2) * leaf_radius)
        glEnd()
    glPopMatrix()


def draw_trees():
    tree_points = [
        (300, 1000), (510, 930), (760, 1050), (1000, 1160), (1350, 930),
        (1780, 1150), (1520, 1540), (1180, 1740), (520, 1480), (320, 1350),
        (260, 430), (650, 650), (1980, 900), (1850, 1600), (1450, 330),
    ]
    
    # Listas de polígonos donde es válido tener árboles
    valid_polys = CAMPUS_BASE_AREAS + GREEN_AREAS + RECTANGULAR_GRAY_AREAS + CONCRETE_AREAS + WALKWAYS
    
    for i, p in enumerate(tree_points):
        # Verificar si el punto está dentro de algún polígono válido
        if any(is_point_in_poly(p, poly) for poly in valid_polys):
            x, z = svg_to_world(p)
            draw_tree(x, z, 0.75 + (i % 3) * 0.18)


def draw_compass():
    glPushMatrix()
    glTranslatef(-18.5, 0.05, -18.0)
    color3((0.10, 0.10, 0.10))
    glLineWidth(3.0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, -2.0)
    glVertex3f(0, 0, 0)
    glVertex3f(1.4, 0, 0)
    glEnd()
    glLineWidth(1.0)
    glPopMatrix()


def point_segment_distance_2d(point, a, b):
    px, pz = point
    ax, az = a
    bx, bz = b
    dx = bx - ax
    dz = bz - az
    length_sq = dx * dx + dz * dz
    if length_sq <= 1e-9:
        return math.hypot(px - ax, pz - az)
    t = ((px - ax) * dx + (pz - az) * dz) / length_sq
    t = max(0.0, min(1.0, t))
    closest_x = ax + dx * t
    closest_z = az + dz * t
    return math.hypot(px - closest_x, pz - closest_z)


def min_fence_distance_world(x, z):
    min_distance = float("inf")
    for area in CAMPUS_FENCE_AREAS:
        world = [svg_to_world(p) for p in area]
        for i, a in enumerate(world):
            b = world[(i + 1) % len(world)]
            min_distance = min(min_distance, point_segment_distance_2d((x, z), a, b))
    return min_distance


def fence_top_height_world(x, z, radius=FENCE_COLLISION_RADIUS):
    if min_fence_distance_world(x, z) < radius:
        return FENCE_BASE_Y + FENCE_BASE_HEIGHT
    return 0.0


def is_blocked_by_fence_world(x, z, y=None, current_x=None, current_z=None):
    fence_top = FENCE_BASE_Y + FENCE_BASE_HEIGHT
    foot_y = y - EYE_HEIGHT if y is not None else None
    if foot_y is not None and foot_y >= fence_top - 0.03:
        return False

    next_distance = min_fence_distance_world(x, z)
    if next_distance >= FENCE_COLLISION_RADIUS:
        return False

    if current_x is not None and current_z is not None:
        current_distance = min_fence_distance_world(current_x, current_z)
        if next_distance >= current_distance - FENCE_SLIDE_EPSILON:
            return False

    return True


def surface_height_world(x, z):
    svg_point = world_to_svg((x, z))
    roof_height = fence_top_height_world(x, z, FENCE_COLLISION_RADIUS * 0.65)
    for _, points, height in BUILDINGS:
        if is_point_in_poly(svg_point, points):
            roof_height = max(roof_height, height * BUILDING_HEIGHT_SCALE)
    return roof_height


def body_surface_height_world(x, z):
    roof_height = 0.0
    for sample_x, sample_z in [
        (x, z),
        (x + COLLISION_RADIUS, z),
        (x - COLLISION_RADIUS, z),
        (x, z + COLLISION_RADIUS),
        (x, z - COLLISION_RADIUS),
    ]:
        roof_height = max(roof_height, surface_height_world(sample_x, sample_z))
        roof_height = max(roof_height, fence_top_height_world(sample_x, sample_z))
    return roof_height


def standing_eye_height(x, z):
    return surface_height_world(x, z) + EYE_HEIGHT


def landing_eye_height(x, z):
    return body_surface_height_world(x, z) + EYE_HEIGHT


def is_inside_building_world(x, z, building_points):
    return is_point_in_poly(world_to_svg((x, z)), building_points)


def body_overlaps_building_world(x, z):
    samples = [
        (x, z),
        (x + COLLISION_RADIUS, z),
        (x - COLLISION_RADIUS, z),
        (x, z + COLLISION_RADIUS),
        (x, z - COLLISION_RADIUS),
    ]
    for sample_x, sample_z in samples:
        svg_point = world_to_svg((sample_x, sample_z))
        if any(is_point_in_poly(svg_point, points) for _, points, _ in BUILDINGS):
            return True
    return False


def is_blocked_world(x, z, y=None, current_x=None, current_z=None):
    if current_x is not None and current_z is not None:
        if surface_height_world(current_x, current_z) > 0.0:
            return False

    samples = [
        (x, z),
        (x + COLLISION_RADIUS, z),
        (x - COLLISION_RADIUS, z),
        (x, z + COLLISION_RADIUS),
        (x, z - COLLISION_RADIUS),
    ]
    for sample in samples:
        svg_point = world_to_svg(sample)
        for _, points, height in BUILDINGS:
            roof_height = height * BUILDING_HEIGHT_SCALE
            foot_y = y - EYE_HEIGHT if y is not None else None
            if foot_y is not None and foot_y >= roof_height - 0.04:
                continue
            if is_point_in_poly(svg_point, points):
                if current_x is not None and current_z is not None:
                    if is_inside_building_world(current_x, current_z, points):
                        continue
                return True
    return False


def try_walk(dx, dz):
    next_x = camera_pos[0] + dx
    next_z = camera_pos[2] + dz

    # Probar por eje permite deslizarse por paredes en vez de quedarse pegado.
    if (
        not is_blocked_world(next_x, camera_pos[2], camera_pos[1], camera_pos[0], camera_pos[2])
        and not is_blocked_by_fence_world(next_x, camera_pos[2], camera_pos[1], camera_pos[0], camera_pos[2])
    ):
        camera_pos[0] = next_x
    if (
        not is_blocked_world(camera_pos[0], next_z, camera_pos[1], camera_pos[0], camera_pos[2])
        and not is_blocked_by_fence_world(camera_pos[0], next_z, camera_pos[1], camera_pos[0], camera_pos[2])
    ):
        camera_pos[2] = next_z


def update_projection(width, height):
    height = max(1, height)
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(72, width / height, 0.05, 200.0)
    glMatrixMode(GL_MODELVIEW)


def framebuffer_size_callback(window, width, height):
    update_projection(width, height)


def init(width, height):
    glClearColor(SKY_COLOR[0], SKY_COLOR[1], SKY_COLOR[2], 1.0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_FLAT)
    update_projection(width, height)


def draw_scene(window):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    yaw = math.radians(camera_yaw)
    pitch = math.radians(camera_pitch)
    
    dir_x = math.cos(pitch) * math.cos(yaw)
    dir_y = math.sin(pitch)
    dir_z = math.cos(pitch) * math.sin(yaw)
    
    eye_y = camera_pos[1]
    if not cenital_view and camera_pos[1] <= EYE_HEIGHT + 0.03:
        eye_y += math.sin(walk_phase) * 0.02 * walk_bob_amount

    look_x = camera_pos[0] + dir_x
    look_y = eye_y + dir_y
    look_z = camera_pos[2] + dir_z
    
    gluLookAt(
        camera_pos[0],
        eye_y,
        camera_pos[2],
        look_x,
        look_y,
        look_z,
        0,
        1,
        0,
    )

    draw_campus_base()
    draw_sports_fields()
    draw_campus_fences()
    draw_buildings()
    draw_trees()
    draw_compass()
    glfw.swap_buffers(window)


def process_input(delta_time):
    global camera_yaw, camera_pitch, walk_phase, walk_bob_amount, flight_mode, roof_descent_mode
    global falling_mode, ground_override_mode, fall_velocity

    frame_speed = camera_speed * delta_time
    vertical_speed = fly_speed * delta_time
    moved = False
    shift_down = keys.get(glfw.KEY_LEFT_SHIFT, False) or keys.get(glfw.KEY_RIGHT_SHIFT, False)
    gesture = current_gesture_command()
    if gesture_mode:
        apply_gesture_mode_switch(gesture["gesture"])

    if cenital_view:
        if gesture_mode and gesture["gesture"] == "peace_sign":
            pan_x = 0.0 if abs(gesture["pan_x"]) < GESTURE_DEADZONE else gesture["pan_x"]
            pan_y = 0.0 if abs(gesture["pan_y"]) < GESTURE_DEADZONE else gesture["pan_y"]
            camera_pos[0] += pan_x * frame_speed * GESTURE_PAN_MULTIPLIER
            camera_pos[2] += pan_y * frame_speed * GESTURE_PAN_MULTIPLIER
            moved = abs(pan_x) > 0.0 or abs(pan_y) > 0.0
        else:
            # En vista cenital, el movimiento es puramente X/Z
            if keys.get(glfw.KEY_W, False):
                camera_pos[2] -= frame_speed
            if keys.get(glfw.KEY_S, False):
                camera_pos[2] += frame_speed
            if keys.get(glfw.KEY_A, False):
                camera_pos[0] -= frame_speed
            if keys.get(glfw.KEY_D, False):
                camera_pos[0] += frame_speed
    else:
        if falling_mode:
            landing_height = landing_eye_height(camera_pos[0], camera_pos[2])
            fall_velocity = min(TERMINAL_FALL_SPEED, fall_velocity + FALL_GRAVITY * delta_time)
            camera_pos[1] -= fall_velocity * delta_time
            if camera_pos[1] <= landing_height:
                camera_pos[1] = landing_height
                falling_mode = False
                fall_velocity = 0.0
                roof_descent_mode = False
                ground_override_mode = landing_height <= EYE_HEIGHT + 0.001 and body_overlaps_building_world(camera_pos[0], camera_pos[2])

        if not flight_mode and not falling_mode:
            surface_height = surface_height_world(camera_pos[0], camera_pos[2])
            if ground_override_mode:
                if surface_height <= 0.0:
                    ground_override_mode = False
                else:
                    camera_pos[1] = EYE_HEIGHT

            if not ground_override_mode and shift_down and surface_height > 0.0:
                roof_descent_mode = True

            if roof_descent_mode:
                camera_pos[1] = max(EYE_HEIGHT, camera_pos[1] - vertical_speed)
                if camera_pos[1] <= EYE_HEIGHT:
                    roof_descent_mode = False
                    ground_override_mode = True
            else:
                target_height = standing_eye_height(camera_pos[0], camera_pos[2])
                if not ground_override_mode:
                    if camera_pos[1] > target_height + 0.05:
                        falling_mode = True
                        fall_velocity = 0.0
                    else:
                        camera_pos[1] = target_height

        if gesture_mode and not flight_mode and gesture["gesture"] == "index_point":
            steer_x = 0.0 if abs(gesture["steer_x"]) < GESTURE_DEADZONE else gesture["steer_x"]
            camera_yaw += steer_x * turn_speed * GESTURE_TURN_MULTIPLIER * delta_time

        yaw = math.radians(camera_yaw)
        forward = [math.cos(yaw), math.sin(yaw)]
        right = [math.cos(yaw + math.pi / 2), math.sin(yaw + math.pi / 2)]
        move_x = 0.0
        move_z = 0.0

        if gesture_mode and not flight_mode and gesture["gesture"] == "index_point":
            move_x += forward[0]
            move_z += forward[1]
        elif not gesture_mode or gesture["gesture"] == "none":
            if keys.get(glfw.KEY_W, False):
                move_x += forward[0]
                move_z += forward[1]
            if keys.get(glfw.KEY_S, False):
                move_x -= forward[0]
                move_z -= forward[1]
            if keys.get(glfw.KEY_A, False):
                move_x -= right[0]
                move_z -= right[1]
            if keys.get(glfw.KEY_D, False):
                move_x += right[0]
                move_z += right[1]

        move_len = math.hypot(move_x, move_z)
        if move_len > 0.0:
            walk_speed = frame_speed
            if gesture_mode and gesture["gesture"] == "index_point":
                walk_speed *= GESTURE_WALK_MULTIPLIER
            try_walk(move_x / move_len * walk_speed, move_z / move_len * walk_speed)
            if not flight_mode and not falling_mode:
                walk_phase += delta_time * 9.0
                walk_bob_amount = min(1.0, walk_bob_amount + delta_time * 8.0)
                if not roof_descent_mode:
                    if ground_override_mode:
                        if surface_height_world(camera_pos[0], camera_pos[2]) <= 0.0:
                            ground_override_mode = False
                        camera_pos[1] = EYE_HEIGHT
                    else:
                        target_height = standing_eye_height(camera_pos[0], camera_pos[2])
                        if camera_pos[1] > target_height + 0.05:
                            falling_mode = True
                            fall_velocity = 0.0
                        else:
                            camera_pos[1] = target_height
            moved = True

        gesture_ascend = gesture_mode and flight_mode and gesture["gesture"] == "open_palm"
        gesture_descend = gesture_mode and flight_mode and gesture["gesture"] == "open_palm_reversed"
        keyboard_ascend = not gesture_mode and flight_mode and keys.get(glfw.KEY_SPACE, False)
        keyboard_descend = not gesture_mode and flight_mode and shift_down

        if gesture_ascend or keyboard_ascend:
            camera_pos[1] += vertical_speed
            moved = True
        if gesture_descend or keyboard_descend:
            landing_height = landing_eye_height(camera_pos[0], camera_pos[2])
            camera_pos[1] = max(landing_height, camera_pos[1] - vertical_speed)
            if camera_pos[1] <= landing_height:
                flight_mode = False
                roof_descent_mode = False
                falling_mode = False
                ground_override_mode = landing_height <= EYE_HEIGHT + 0.001 and body_overlaps_building_world(camera_pos[0], camera_pos[2])
                fall_velocity = 0.0
            moved = True

    if cenital_view:
        if keys.get(glfw.KEY_KP_8, False):
            camera_pos[1] += frame_speed
        if keys.get(glfw.KEY_KP_2, False):
            camera_pos[1] = max(6.0, camera_pos[1] - frame_speed)
    
    if not cenital_view:
        if keys.get(glfw.KEY_LEFT, False):
            camera_yaw -= turn_speed * delta_time
        if keys.get(glfw.KEY_RIGHT, False):
            camera_yaw += turn_speed * delta_time
        if keys.get(glfw.KEY_UP, False):
            camera_pitch = min(28.0, camera_pitch + turn_speed * delta_time)
        if keys.get(glfw.KEY_DOWN, False):
            camera_pitch = max(-65.0, camera_pitch - turn_speed * delta_time)

    if not moved:
        walk_bob_amount = max(0.0, walk_bob_amount - delta_time * 10.0)


def print_usage_tutorial():
    print(
        """
Controles - Campus ITM 3D
=========================
Movimiento:
  W / A / S / D        Caminar o desplazarse en vista cenital
  Mouse                Mirar alrededor en modo persona
  Flechas izquierda/derecha  Girar camara con teclado
  Flechas arriba/abajo       Inclinar camara con teclado

Vuelo creativo:
  Doble Space          Activar/desactivar vuelo
  Space                Subir mientras el vuelo esta activo
  Shift izquierdo/derecho    Bajar mientras el vuelo esta activo
  Shift sobre techo    Bajar del techo al suelo
  Rueda del mouse      Ajustar altura en vuelo o vista cenital

Vistas y modos:
  G                    Activar/desactivar control por gestos
  C                    Alternar vista cenital / persona
  KP_8 / KP_2          Subir/bajar camara en vista cenital
  M                    Alternar modo naranja / institucional

Gestos con una mano:
  Normal               Indice extendido: camina y gira al moverlo a los lados
  Vuelo creativo       Palma abierta hacia la camara: subir; palma volteada hacia ti: bajar
  Vista cenital        Amor y paz: mover la mano desplaza la camara
  Sin mano             Vuelve a modo persona normal

Sistema:
  Esc                  Salir
"""
    )


def main():
    if not glfw.init():
        sys.exit("No se pudo inicializar GLFW.")

    width, height = 1100, 760
    window = glfw.create_window(width, height, "Campus ITM 3D - primitivas OpenGL", None, None)
    if not window:
        glfw.terminate()
        sys.exit("No se pudo crear la ventana.")

    print_usage_tutorial()

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    glfw.swap_interval(1)
    framebuffer_width, framebuffer_height = glfw.get_framebuffer_size(window)
    init(framebuffer_width, framebuffer_height)

    previous_time = glfw.get_time()
    while not glfw.window_should_close(window):
        current_time = glfw.get_time()
        delta_time = min(current_time - previous_time, 0.05)
        previous_time = current_time

        process_input(delta_time)
        draw_scene(window)
        glfw.poll_events()

    if gesture_controller is not None:
        gesture_controller.stop()
    glfw.terminate()


if __name__ == "__main__":
    main()
