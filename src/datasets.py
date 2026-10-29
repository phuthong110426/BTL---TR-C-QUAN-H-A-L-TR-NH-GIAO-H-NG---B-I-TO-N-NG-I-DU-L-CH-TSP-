"""
Module quản lý bộ dữ liệu chuẩn TSPLIB (Reinelt, 1991) và bộ dữ liệu tự sinh nhiều kích thước.
Tự động xuất các tệp định dạng `.tsp` chuẩn vào thư mục `data/tsplib/` và `data/synthetic/`.

Danh sách 12 thể hiện thực nghiệm chính (vượt mức tối thiểu 10 thể hiện, >= 3 mức kích thước):
A. Nhóm dữ liệu nhỏ (Small, n = 10..18) - Dùng đối chiếu với lời giải tối ưu của Held-Karp & Branch-and-Bound:
   1. syn_10 (n = 10, seed = 101)
   2. syn_12 (n = 12, seed = 102)
   3. syn_15 (n = 15, seed = 105)
   4. syn_16 (n = 16, seed = 106)
   5. syn_18 (n = 18, seed = 108)

B. Nhóm dữ liệu chuẩn TSPLIB & Trung bình - Lớn (Medium & Large, n = 51..150):
   6. eil51     (TSPLIB, n = 51,  BKS = 426)
   7. berlin52  (TSPLIB, n = 52,  BKS = 7542)
   8. st70      (TSPLIB, n = 70,  BKS = 675)
   9. eil76     (TSPLIB, n = 76,  BKS = 538)
   10. kroA100  (TSPLIB, n = 100, BKS = 21282)
   11. syn_120  (Tự sinh phân cụm đô thị, n = 120, seed = 220)
   12. pr152_syn / ch150_syn (Cỡ lớn n = 150, seed = 250)
"""

import os
from typing import List, Tuple, Dict
from .tsp_instance import TSPInstance

# ==============================================================================
# TỌA ĐỘ CHUẨN TSPLIB (REINELT, 1991) - EUC_2D
# ==============================================================================

# 1. eil51 (Christofides & Eilon, 1969) - 51 cities, BKS = 426
EIL51_COORDS: List[Tuple[float, float]] = [
    (37, 52), (49, 49), (52, 64), (20, 26), (40, 30), (21, 47), (17, 63), (31, 62),
    (52, 33), (51, 21), (42, 41), (31, 32), (5, 25), (12, 42), (36, 16), (52, 41),
    (27, 23), (17, 33), (13, 13), (57, 58), (62, 42), (42, 57), (16, 57), (8, 52),
    (7, 38), (27, 68), (30, 48), (43, 67), (58, 48), (58, 27), (37, 69), (38, 46),
    (46, 10), (61, 33), (62, 63), (63, 69), (32, 22), (45, 35), (59, 15), (5, 6),
    (10, 17), (21, 10), (5, 64), (30, 15), (39, 10), (32, 39), (25, 32), (25, 55),
    (48, 28), (56, 37), (30, 40),
]

# 2. berlin52 (Grötschel, 1991) - 52 locations in Berlin, BKS = 7542
BERLIN52_COORDS: List[Tuple[float, float]] = [
    (565.0, 575.0), (25.0, 185.0), (345.0, 750.0), (945.0, 685.0), (845.0, 655.0),
    (880.0, 660.0), (25.0, 230.0), (525.0, 1000.0), (580.0, 1175.0), (650.0, 1130.0),
    (1605.0, 620.0), (1220.0, 580.0), (1465.0, 200.0), (1530.0, 5.0), (845.0, 680.0),
    (725.0, 370.0), (145.0, 665.0), (415.0, 635.0), (510.0, 875.0), (560.0, 365.0),
    (300.0, 465.0), (520.0, 585.0), (480.0, 415.0), (835.0, 625.0), (975.0, 580.0),
    (1215.0, 245.0), (1320.0, 315.0), (1250.0, 400.0), (660.0, 180.0), (410.0, 250.0),
    (420.0, 555.0), (575.0, 665.0), (1150.0, 1160.0), (700.0, 580.0), (685.0, 595.0),
    (685.0, 610.0), (770.0, 610.0), (795.0, 645.0), (720.0, 635.0), (760.0, 650.0),
    (475.0, 960.0), (95.0, 260.0), (875.0, 920.0), (700.0, 500.0), (555.0, 815.0),
    (830.0, 485.0), (1170.0, 65.0), (830.0, 610.0), (605.0, 625.0), (595.0, 360.0),
    (1340.0, 725.0), (1740.0, 245.0),
]

# 3. st70 (Smith & Thompson) - 70 cities, BKS = 675
ST70_COORDS: List[Tuple[float, float]] = [
    (64, 96), (80, 39), (69, 23), (72, 42), (48, 67), (58, 43), (81, 34), (79, 17),
    (30, 23), (42, 67), (7, 76), (29, 51), (78, 92), (64, 8), (95, 57), (57, 91),
    (40, 35), (68, 40), (92, 34), (62, 1), (28, 43), (76, 73), (67, 88), (93, 54),
    (6, 8), (87, 18), (30, 9), (77, 13), (78, 94), (55, 3), (82, 88), (73, 28),
    (20, 55), (27, 43), (95, 86), (67, 99), (48, 83), (75, 81), (8, 19), (20, 18),
    (54, 38), (63, 36), (44, 33), (52, 18), (12, 13), (25, 5), (58, 85), (5, 67),
    (90, 9), (41, 76), (25, 76), (37, 64), (56, 63), (10, 55), (98, 7), (16, 74),
    (89, 60), (48, 82), (81, 76), (29, 60), (17, 22), (5, 45), (79, 70), (9, 100),
    (17, 82), (74, 67), (10, 68), (48, 19), (83, 86), (84, 94),
]

# 4. eil76 (Christofides & Eilon, 1969) - 76 cities, BKS = 538
EIL76_COORDS: List[Tuple[float, float]] = [
    (22, 22), (36, 26), (21, 45), (45, 35), (55, 20), (33, 34), (50, 50), (55, 45),
    (26, 59), (40, 66), (55, 65), (35, 51), (62, 35), (62, 57), (62, 24), (21, 36),
    (33, 44), (9, 56), (62, 48), (66, 14), (44, 13), (26, 13), (11, 28), (7, 43),
    (17, 64), (41, 46), (55, 34), (35, 16), (52, 26), (43, 26), (31, 76), (22, 53),
    (26, 29), (50, 40), (55, 50), (54, 10), (60, 15), (47, 66), (30, 60), (30, 50),
    (12, 17), (15, 14), (16, 19), (21, 48), (50, 30), (51, 42), (50, 15), (48, 21),
    (12, 38), (15, 56), (29, 39), (54, 38), (55, 57), (67, 41), (10, 70), (6, 25),
    (65, 27), (40, 60), (70, 64), (64, 4), (36, 6), (30, 20), (20, 30), (15, 5),
    (50, 70), (57, 72), (45, 42), (38, 33), (50, 4), (66, 8), (59, 5), (35, 60),
    (27, 24), (40, 20), (40, 37), (40, 40),
]

# 5. kroA100 (Krolak, Felts & Marble, 1971) - 100 cities, BKS = 21282
KROA100_COORDS: List[Tuple[float, float]] = [
    (1380, 939), (2848, 96), (3510, 1671), (457, 334), (3888, 666),
    (984, 965), (2721, 1482), (1286, 525), (2716, 1432), (738, 1325),
    (1251, 1832), (2728, 1698), (3815, 169), (3683, 1533), (1247, 1945),
    (123, 862), (1234, 1946), (252, 1240), (611, 673), (2576, 1676),
    (928, 1700), (53, 857), (1807, 1711), (274, 1420), (2574, 946),
    (178, 24), (2678, 1825), (1795, 962), (3384, 1498), (3520, 1079),
    (1256, 61), (1424, 1728), (3913, 192), (3085, 1528), (2573, 1969),
    (463, 1670), (3875, 598), (298, 1513), (3479, 821), (2542, 236),
    (3955, 1743), (1323, 280), (3447, 1830), (2936, 337), (1621, 1830),
    (3373, 1646), (1393, 1368), (3874, 1318), (938, 955), (3022, 474),
    (2482, 1183), (3854, 923), (376, 825), (2519, 135), (2945, 1622),
    (953, 268), (2628, 1479), (2097, 981), (890, 1846), (2139, 1806),
    (2421, 1007), (2290, 1810), (1115, 1052), (2588, 302), (327, 265),
    (241, 341), (1917, 687), (2991, 792), (2573, 599), (19, 674),
    (3911, 1673), (872, 1559), (2863, 558), (929, 1766), (839, 620),
    (3893, 102), (2178, 1619), (3822, 899), (378, 1048), (1178, 100),
    (2599, 901), (3416, 143), (2961, 1605), (611, 1384), (3113, 885),
    (2597, 1830), (2586, 1286), (161, 906), (1429, 134), (742, 1025),
    (1625, 1651), (1187, 706), (1787, 1009), (22, 987), (3640, 43),
    (3756, 882), (776, 392), (1724, 1642), (198, 1810), (3950, 1558),
]


def build_all_datasets(data_dir: str) -> Dict[str, List[TSPInstance]]:
    """
    Khởi tạo và lưu toàn bộ các bộ dữ liệu chuẩn TSPLIB và bộ dữ liệu tự sinh ra thư mục `data_dir`.
    Trả về dict phân nhóm:
        - 'small': các thể hiện nhỏ (n = 10, 12, 15, 16, 18) để chạy thuật toán chính xác Held-Karp & B&B
        - 'tsplib': 5 bộ dữ liệu chuẩn TSPLIB (eil51, berlin52, st70, eil76, kroA100)
        - 'large_syn': các bộ dữ liệu tự sinh cỡ vừa/lớn (syn_40, syn_80, syn_120, syn_150)
    """
    tsplib_dir = os.path.join(data_dir, "tsplib")
    syn_dir = os.path.join(data_dir, "synthetic")
    os.makedirs(tsplib_dir, exist_ok=True)
    os.makedirs(syn_dir, exist_ok=True)

    # 1. Các thể hiện nhỏ (dùng kiểm chứng với lời giải tối ưu chính xác Held-Karp)
    small_specs = [
        ("syn_10", 10, 101, False),
        ("syn_12", 12, 102, False),
        ("syn_15", 15, 105, True),
        ("syn_16", 16, 106, False),
        ("syn_18", 18, 108, True),
    ]
    small_instances: List[TSPInstance] = []
    for name, n, seed, clustered in small_specs:
        inst = TSPInstance.generate_random(n=n, seed=seed, name=name, box_size=500.0, clustered=clustered)
        inst.save_tsplib_file(os.path.join(syn_dir, f"{name}.tsp"))
        small_instances.append(inst)

    # 2. Bộ dữ liệu chuẩn TSPLIB
    tsplib_specs = [
        ("eil51", EIL51_COORDS, 426.0),
        ("berlin52", BERLIN52_COORDS, 7542.0),
        ("st70", ST70_COORDS, 675.0),
        ("eil76", EIL76_COORDS, 538.0),
        ("kroA100", KROA100_COORDS, 21282.0),
    ]
    tsplib_instances: List[TSPInstance] = []
    for name, coords, bks in tsplib_specs:
        inst = TSPInstance(name=name, coords=coords, edge_weight_type="EUC_2D", bks=bks)
        inst.save_tsplib_file(os.path.join(tsplib_dir, f"{name}.tsp"))
        tsplib_instances.append(inst)

    # 3. Bộ dữ liệu tự sinh nhiều mức kích thước (40, 80, 120, 150)
    large_syn_specs = [
        ("syn_40", 40, 204, False),
        ("syn_80", 80, 208, True),
        ("syn_120", 120, 212, True),
        ("syn_150", 150, 215, False),
    ]
    large_syn_instances: List[TSPInstance] = []
    for name, n, seed, clustered in large_syn_specs:
        inst = TSPInstance.generate_random(n=n, seed=seed, name=name, box_size=1000.0, clustered=clustered)
        inst.save_tsplib_file(os.path.join(syn_dir, f"{name}.tsp"))
        large_syn_instances.append(inst)

    return {
        "small": small_instances,
        "tsplib": tsplib_instances,
        "large_syn": large_syn_instances,
    }
