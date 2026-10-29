"""
Module định nghĩa cấu trúc dữ liệu bài toán Người du lịch (TSP)
Hỗ trợ đọc tệp chuẩn TSPLIB (.tsp), sinh dữ liệu ngẫu nhiên có kiểm soát (seed),
và sử dụng danh sách láng giềng gần (Candidate List) cho các thể hiện lớn.
"""

import math
import random
import os
from typing import List, Tuple, Optional, Dict


class TSPInstance:
    """
    Biểu diễn một thể hiện (instance) của bài toán TSP đối xứng.
    """

    def __init__(
        self,
        name: str,
        coords: List[Tuple[float, float]],
        edge_weight_type: str = "EUC_2D",
        bks: Optional[float] = None,
        dist_matrix: Optional[List[List[float]]] = None,
        candidate_k: int = 20,
    ):
        self.name = name
        self.coords = coords
        self.n = len(coords) if coords else (len(dist_matrix) if dist_matrix else 0)
        self.edge_weight_type = edge_weight_type.upper()
        self.bks = bks

        if dist_matrix is not None:
            self.dist_matrix = dist_matrix
        else:
            self.dist_matrix = self._compute_distance_matrix()

        # Xây dựng danh sách láng giềng gần nhất (Candidate List) cho mỗi đỉnh
        # Giúp tăng tốc tìm kiếm cục bộ và ACO trên dữ liệu lớn (n >= 100..1000)
        self.candidate_k = min(candidate_k, max(1, self.n - 1))
        self.candidates: List[List[int]] = self._build_candidate_lists(self.candidate_k)

    @staticmethod
    def _nint(x: float) -> int:
        """Làm tròn số nguyên theo chuẩn TSPLIB: floor(x + 0.5)."""
        return int(math.floor(x + 0.5))

    def _compute_distance_matrix(self) -> List[List[float]]:
        n = self.n
        mat = [[0.0] * n for _ in range(n)]
        for i in range(n):
            x1, y1 = self.coords[i]
            for j in range(i + 1, n):
                x2, y2 = self.coords[j]
                dx = x1 - x2
                dy = y1 - y2
                d = math.hypot(dx, dy)
                if self.edge_weight_type == "EUC_2D":
                    # Chuẩn TSPLIB EUC_2D làm tròn khoảng cách về số nguyên gần nhất
                    val = float(self._nint(d))
                else:
                    val = round(d, 4)
                mat[i][j] = val
                mat[j][i] = val
        return mat

    def _build_candidate_lists(self, k: int) -> List[List[int]]:
        n = self.n
        cand = []
        for i in range(n):
            row = self.dist_matrix[i]
            neighbors = [j for j in range(n) if j != i]
            neighbors.sort(key=lambda j: row[j])
            cand.append(neighbors[:k])
        return cand

    def distance(self, u: int, v: int) -> float:
        return self.dist_matrix[u][v]

    def tour_cost(self, tour: List[int]) -> float:
        """Tính tổng độ dài chu trình đi qua các đỉnh trong `tour` và quay về đỉnh đầu."""
        n = self.n
        if len(tour) != n:
            raise ValueError(f"Độ dài chu trình ({len(tour)}) khác số đỉnh n ({n}).")
        total = 0.0
        mat = self.dist_matrix
        for i in range(n - 1):
            total += mat[tour[i]][tour[i + 1]]
        total += mat[tour[-1]][tour[0]]
        return total

    @classmethod
    def from_tsplib_file(cls, filepath: str, bks: Optional[float] = None) -> "TSPInstance":
        """Đọc tệp định dạng chuẩn TSPLIB (.tsp)."""
        name = os.path.splitext(os.path.basename(filepath))[0]
        edge_weight_type = "EUC_2D"
        coords: List[Tuple[float, float]] = []
        reading_coords = False
        file_bks = bks

        with open(filepath, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                if line.upper().startswith("EOF"):
                    break
                if not reading_coords:
                    if line.upper().startswith("NAME"):
                        parts = line.split(":")
                        if len(parts) > 1:
                            name = parts[1].strip()
                    elif line.upper().startswith("COMMENT"):
                        # Cho phép đọc BKS nếu được ghi trong COMMENT: BKS=7542
                        if "BKS=" in line.upper():
                            try:
                                bks_str = line.upper().split("BKS=")[1].split()[0].strip(",;)")
                                if file_bks is None:
                                    file_bks = float(bks_str)
                            except ValueError:
                                pass
                    elif line.upper().startswith("EDGE_WEIGHT_TYPE"):
                        parts = line.split(":")
                        if len(parts) > 1:
                            edge_weight_type = parts[1].strip()
                    elif line.upper().startswith("NODE_COORD_SECTION"):
                        reading_coords = True
                else:
                    parts = line.split()
                    if len(parts) >= 3:
                        x = float(parts[1])
                        y = float(parts[2])
                        coords.append((x, y))

        return cls(name=name, coords=coords, edge_weight_type=edge_weight_type, bks=file_bks)

    def save_tsplib_file(self, filepath: str) -> None:
        """Lưu thể hiện ra tệp chuẩn .tsp."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"NAME : {self.name}\n")
            bks_comment = f" (BKS={self.bks})" if self.bks is not None else ""
            f.write(f"COMMENT : TSP Instance {self.name}{bks_comment}\n")
            f.write("TYPE : TSP\n")
            f.write(f"DIMENSION : {self.n}\n")
            f.write(f"EDGE_WEIGHT_TYPE : {self.edge_weight_type}\n")
            f.write("NODE_COORD_SECTION\n")
            for idx, (x, y) in enumerate(self.coords, start=1):
                f.write(f"{idx} {x:.4f} {y:.4f}\n")
            f.write("EOF\n")

    @classmethod
    def generate_random(
        cls,
        n: int,
        seed: int = 42,
        name: Optional[str] = None,
        box_size: float = 1000.0,
        clustered: bool = False,
    ) -> "TSPInstance":
        """
        Tự sinh thể hiện TSP ngẫu nhiên có kiểm soát bằng `seed`.
        Hỗ trợ phân bố đều (uniform) hoặc phân cụm (clustered) mô phỏng giao hàng đô thị.
        """
        rng = random.Random(seed)
        if name is None:
            name = f"syn_{n}_s{seed}"
        coords: List[Tuple[float, float]] = []
        if not clustered:
            for _ in range(n):
                x = round(rng.uniform(0.0, box_size), 2)
                y = round(rng.uniform(0.0, box_size), 2)
                coords.append((x, y))
        else:
            num_clusters = max(2, min(8, n // 10))
            centers = [
                (rng.uniform(0.15 * box_size, 0.85 * box_size), rng.uniform(0.15 * box_size, 0.85 * box_size))
                for _ in range(num_clusters)
            ]
            sigma = box_size * 0.08
            for i in range(n):
                cx, cy = centers[i % num_clusters]
                x = round(max(0.0, min(box_size, rng.gauss(cx, sigma))), 2)
                y = round(max(0.0, min(box_size, rng.gauss(cy, sigma))), 2)
                coords.append((x, y))

        return cls(name=name, coords=coords, edge_weight_type="EUC_2D", bks=None)
