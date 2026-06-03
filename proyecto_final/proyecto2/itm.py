import math
import sys

import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluLookAt, gluPerspective


SVG_W, SVG_H = 2213.0, 2135.0
SCALE = 70.0

keys = {}
cenital_view = False
unified_buildings = False
camera_pos = [2.0, 24.0, 34.0]
camera_yaw = -92.0
camera_pitch = -23.0
camera_speed = 0.45
turn_speed = 1.8

GRAY_SURFACE = (0.82, 0.82, 0.82)
EDGE_COLOR = (0.09, 0.09, 0.09)
CAMPUS_LAWN_COLOR = (0.77, 0.88, 0.70)
LAWN_COLOR = (0.77, 0.88, 0.70)
FIELD_COLOR = (0.62, 0.80, 0.22)
TRACK_COLOR = (0.73, 0.56, 0.29)
GROUND_COLOR = (1.0, 1.0, 1.0)
GREEN_Y = 0.01
BASE_GREEN_Y = 0.005
GRAY_Y = 0.045
EDGE_Y = 0.07
SPORT_Y = 0.085


CAMPUS_BASE_AREAS = [
    # Area 1: Bloque occidental (trapezoide refinado)
    [(140, 180), (580, 180), (220, 1020), (140, 1020)],
    # Area 2: Bloque central y oriental (polígono principal siguiendo vialidad)
    [(1050, 260), (1850, 320), (2000, 850), (1850, 1450), (1650, 1950), (1150, 1750), (250, 1300), (750, 650)],
    # Area 3: Bloque sur-oriental (triángulo refinado)
    [(1750, 1800), (2200, 1950), (2020, 2130), (1700, 2040)],
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
    [(1760, 1800), (2208, 1945), (2015, 2132), (1708, 2042)],
    # Nuevos triángulos de relleno (Modificación quirúrgica solicitada)
    [(580, 180), (781, 257), (220, 1020)],
    [(1750, 1800), (1917, 1585), (2200, 1950)],
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
    [(1978, 1952), (1988, 1927), (1936, 1910), (1927, 1935)],
    [(1868, 1959), (1912, 1977), (1895, 2014), (1851, 1996)],
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
    [(1796, 1836), (1995, 1831), (1964, 1905), (1827, 1888)],
    [(1868, 1959), (1912, 1977), (1895, 2014), (1851, 1996)],
    [(1880, 1875), (1978, 1910), (1942, 1990), (1845, 1954)],
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
    [(1827, 1761), (1995, 1831), (1964, 1905), (1796, 1836)],
    [(738, 1589), (750, 1594), (677, 1761), (665, 1756)],
]


BUILDINGS = [
    ("3a", [(1800, 1836), (1888, 1872), (1853, 1949), (1764, 1913)], 1.1),
    ("3b", [(1948, 1738), (2019, 1767), (1995, 1823), (1924, 1794)], 1.0),
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
    ("ene", [(726, 1119), (781, 1120), (780, 1181), (725, 1180)], 1.3),
    ("p", [(790, 1179), (852, 1181), (851, 1215), (789, 1214)], 1.0),
    ("r", [(1012, 1241), (1067, 1242), (1066, 1314), (1011, 1313)], 1.3),
    ("v", [(1115, 1245), (1141, 1245), (1140, 1328), (1114, 1328)], 1.1),
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
    ("w", [(1151, 1240), (1176, 1241), (1175, 1287), (1150, 1287)], 0.9),
    ("ac", [(1134, 1497), (1206, 1498), (1206, 1530), (1133, 1528)], 1.0),
    ("ad", [(1133, 1573), (1201, 1574), (1200, 1607), (1133, 1606)], 1.0),
    ("i", [(1016, 874), (1137, 876), (1134, 993), (1014, 990)], 1.6),
    ("s", [(444, 1267), (472, 1268), (472, 1292), (599, 1294), (599, 1269), (444, 1267)], 0.9),
    ("d", [(1096, 581), (1259, 584), (1258, 623), (1095, 620)], 1.0),
    ("z", [(1193, 1252), (1229, 1253), (1228, 1311), (1246, 1312), (1245, 1338), (1190, 1337), (1191, 1311)], 1.0),
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
    ("ll", [(878, 1202), (975, 1204), (973, 1288), (876, 1286)], 1.4),
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


def key_callback(window, key, scancode, action, mods):
    global cenital_view, camera_pitch, camera_yaw, unified_buildings
    if action == glfw.PRESS:
        keys[key] = True
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        if key == glfw.KEY_M:
            unified_buildings = not unified_buildings
            print(f"Edificios Unificados: {'ON' if unified_buildings else 'OFF'}")
        if key == glfw.KEY_C:
            cenital_view = not cenital_view
            if cenital_view:
                camera_pitch = -89.0
                camera_yaw = -90.0
                print("Vista Cenital: ON")
            else:
                camera_pitch = -23.0
                print("Vista Cenital: OFF")
    elif action == glfw.RELEASE:
        keys[key] = False


def cursor_pos_callback(window, xpos, ypos):
    pass


def mouse_button_callback(window, button, action, mods):
    pass


def scroll_callback(window, xoffset, yoffset):
    camera_pos[1] = max(2.5, camera_pos[1] + yoffset * camera_speed * 2.0)


def svg_to_world(point):
    x, y = point
    return ((x - SVG_W * 0.5) / SCALE, (y - SVG_H * 0.5) / SCALE)


def world_to_svg(point):
    x, z = point
    return (x * SCALE + SVG_W * 0.5, z * SCALE + SVG_H * 0.5)


def color3(color):
    glColor3f(color[0], color[1], color[2])


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
    draw_line_loop(points, (0.96, 0.96, 0.92), SPORT_Y + 0.03, 2.0)

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
    glVertex3f(m1[0], SPORT_Y + 0.04, m1[1])
    glVertex3f(m2[0], SPORT_Y + 0.04, m2[1])
    glEnd()

    cx = (a[0] + b[0] + c[0] + d[0]) / 4.0
    cz = (a[1] + b[1] + c[1] + d[1]) / 4.0
    circle = [(cx + math.cos(i * 2 * math.pi / 48) * 0.55, cz + math.sin(i * 2 * math.pi / 48) * 0.55) for i in range(48)]
    draw_polyline_world(circle, (0.96, 0.96, 0.92), SPORT_Y + 0.05, 1.4, True)

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
        draw_polyline_world([box_a, box_b, box_c, box_d], (0.96, 0.96, 0.92), SPORT_Y + 0.05, 1.2, True)


def draw_prism(points, height, wall_color, roof_color):
    world = [svg_to_world(p) for p in points]
    
    if unified_buildings:
        # Modo Unificado: Un solo color y base alineada con el concreto
        base_color = roof_color
        color3(base_color)
        glBegin(GL_QUADS)
        for i, (x1, z1) in enumerate(world):
            x2, z2 = world[(i + 1) % len(world)]
            glVertex3f(x1, GRAY_Y, z1)
            glVertex3f(x2, GRAY_Y, z2)
            glVertex3f(x2, height, z2)
            glVertex3f(x1, height, z1)
        glEnd()

        glBegin(GL_POLYGON)
        for x, z in world:
            glVertex3f(x, height, z)
        glEnd()
    else:
        # Modo Clásico: Paredes y techos distintos con contorno
        color3(wall_color)
        glBegin(GL_QUADS)
        for i, (x1, z1) in enumerate(world):
            x2, z2 = world[(i + 1) % len(world)]
            glVertex3f(x1, 0.03, z1)
            glVertex3f(x2, 0.03, z2)
            glVertex3f(x2, height, z2)
            glVertex3f(x1, height, z1)
        glEnd()

        color3(roof_color)
        glBegin(GL_POLYGON)
        for x, z in world:
            glVertex3f(x, height, z)
        glEnd()
        draw_line_loop(points, (0.12, 0.10, 0.08), height + 0.01, 1.0)


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


def draw_buildings():
    for name, points, height in BUILDINGS:
        tall = name in {"a", "i", "h", "af", "ag", "ah", "y"}
        wall = (0.86, 0.50, 0.22) if not tall else (0.78, 0.40, 0.18)
        roof = (0.96, 0.66, 0.32) if not tall else (0.90, 0.54, 0.24)
        draw_prism(points, height, wall, roof)

        if height > 1.25:
            draw_window_band(points, height)


def draw_window_band(points, height):
    world = [svg_to_world(p) for p in points]
    color3((0.20, 0.24, 0.28))
    glBegin(GL_LINES)
    for i in range(len(world)):
        x1, z1 = world[i]
        x2, z2 = world[(i + 1) % len(world)]
        mx1 = x1 * 0.72 + x2 * 0.28
        mz1 = z1 * 0.72 + z2 * 0.28
        mx2 = x1 * 0.28 + x2 * 0.72
        mz2 = z1 * 0.28 + z2 * 0.72
        glVertex3f(mx1, height * 0.55, mz1)
        glVertex3f(mx2, height * 0.55, mz2)
    glEnd()


def draw_sports_fields():
    # Pista atletica y campo grande oriental.
    draw_ellipse(1780, 916, 215, 430, TRACK_COLOR, SPORT_Y, 96)
    draw_ellipse(1780, 916, 150, 350, FIELD_COLOR, SPORT_Y + 0.01, 96)
    draw_polyline_world(ellipse_points(1780, 916, 215, 430, 96), EDGE_COLOR, SPORT_Y + 0.04, 1.0, True)
    draw_polyline_world(ellipse_points(1780, 916, 150, 350, 96), EDGE_COLOR, SPORT_Y + 0.04, 1.0, True)
    draw_field([(1668, 664), (1890, 668), (1880, 1225), (1658, 1220)])

    # Canchas al sur del campus principal.
    draw_field([(1415, 1510), (1768, 1518), (1763, 1706), (1410, 1698)])
    draw_field([(1462, 1805), (1628, 1809), (1624, 1910), (1458, 1906)])

    # Canchas rectangulares del centro-oriente.
    for points in [
        [(1395, 1158), (1535, 1160), (1531, 1265), (1392, 1262)],
        [(1352, 1298), (1518, 1301), (1514, 1436), (1348, 1432)],
        [(1948, 1868), (2102, 1930), (2066, 2010), (1912, 1948)],
    ]:
        draw_flat_polygon(points, BASE_GREEN_COLOR, SPORT_Y)
        draw_line_loop(points, (0.96, 0.96, 0.92), SPORT_Y + 0.04, 1.5)


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
    height = 0.45
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


def init(width, height):
    glClearColor(GROUND_COLOR[0], GROUND_COLOR[1], GROUND_COLOR[2], 1.0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_FLAT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, width / height, 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW)


def draw_scene(window):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    yaw = math.radians(camera_yaw)
    pitch = math.radians(camera_pitch)
    
    dir_x = math.cos(pitch) * math.cos(yaw)
    dir_y = math.sin(pitch)
    dir_z = math.cos(pitch) * math.sin(yaw)
    
    look_x = camera_pos[0] + dir_x
    look_y = camera_pos[1] + dir_y
    look_z = camera_pos[2] + dir_z
    
    gluLookAt(
        camera_pos[0],
        camera_pos[1],
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
    draw_buildings()
    draw_trees()
    draw_compass()
    glfw.swap_buffers(window)


def process_input():
    global camera_yaw, camera_pitch

    if cenital_view:
        # En vista cenital, el movimiento es puramente X/Z
        if keys.get(glfw.KEY_W, False):
            camera_pos[2] -= camera_speed
        if keys.get(glfw.KEY_S, False):
            camera_pos[2] += camera_speed
        if keys.get(glfw.KEY_A, False):
            camera_pos[0] -= camera_speed
        if keys.get(glfw.KEY_D, False):
            camera_pos[0] += camera_speed
    else:
        yaw = math.radians(camera_yaw)
        forward = [math.cos(yaw), math.sin(yaw)]
        right = [math.cos(yaw + math.pi / 2), math.sin(yaw + math.pi / 2)]

        if keys.get(glfw.KEY_W, False):
            camera_pos[0] += forward[0] * camera_speed
            camera_pos[2] += forward[1] * camera_speed
        if keys.get(glfw.KEY_S, False):
            camera_pos[0] -= forward[0] * camera_speed
            camera_pos[2] -= forward[1] * camera_speed
        if keys.get(glfw.KEY_A, False):
            camera_pos[0] -= right[0] * camera_speed
            camera_pos[2] -= right[1] * camera_speed
        if keys.get(glfw.KEY_D, False):
            camera_pos[0] += right[0] * camera_speed
            camera_pos[2] += right[1] * camera_speed

    if keys.get(glfw.KEY_KP_8, False):
        camera_pos[1] += camera_speed
    if keys.get(glfw.KEY_KP_2, False):
        camera_pos[1] = max(2.5, camera_pos[1] - camera_speed)
    
    if not cenital_view:
        if keys.get(glfw.KEY_LEFT, False):
            camera_yaw -= turn_speed
        if keys.get(glfw.KEY_RIGHT, False):
            camera_yaw += turn_speed
        if keys.get(glfw.KEY_UP, False):
            camera_pitch = min(8.0, camera_pitch + turn_speed)
        if keys.get(glfw.KEY_DOWN, False):
            camera_pitch = max(-82.0, camera_pitch - turn_speed)


def main():
    if not glfw.init():
        sys.exit("No se pudo inicializar GLFW.")

    width, height = 1100, 760
    window = glfw.create_window(width, height, "Campus ITM 3D - primitivas OpenGL", None, None)
    if not window:
        glfw.terminate()
        sys.exit("No se pudo crear la ventana.")

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glViewport(0, 0, width, height)
    init(width, height)

    while not glfw.window_should_close(window):
        process_input()
        draw_scene(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()
main()
