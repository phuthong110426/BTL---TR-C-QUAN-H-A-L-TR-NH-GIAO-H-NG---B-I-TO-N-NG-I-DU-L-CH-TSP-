"""
Mục 3.1.2: Các thuật toán Heuristic xây dựng (Constructive Heuristics) cho bài toán TSP.
Bao gồm:
1. Láng giềng gần nhất (Nearest Neighbor - NN): O(n^2)
2. Láng giềng gần nhất đa điểm xuất phát (Multi-Start Nearest Neighbor): O(k * n^2)
3. Chèn rẻ nhất (Cheapest Insertion - CI): O(n^3) (tối ưu hóa bước tìm vị trí chèn trong O(n^2))
"""

import time
from typing import List, Tuple
from .tsp_instance import TSPInstance
from .validator import assert_valid_tour


def nearest_neighbor(
    instance: TSPInstance,
    start_node: int = 0,
) -> Tuple[List[int], float, float]:
    """
    Thuật toán tham lam Láng giềng gần nhất (Nearest Neighbor).
    Bắt đầu từ `start_node`, ở mỗi bước chọn đỉnh chưa thăm gần nhất với đỉnh hiện tại.
    Độ phức tạp thời gian: O(n^2), không gian: O(n).
    """
    t0 = time.perf_counter()
    n = instance.n
    mat = instance.dist_matrix

    visited = [False] * n
    tour = [start_node]
    visited[start_node] = True
    curr = start_node
    total_cost = 0.0

    for _ in range(n - 1):
        row = mat[curr]
        best_next = -1
        best_dist = float("inf")
        for nxt in range(n):
            if not visited[nxt] and row[nxt] < best_dist:
                best_dist = row[nxt]
                best_next = nxt
        visited[best_next] = True
        tour.append(best_next)
        total_cost += best_dist
        curr = best_next

    total_cost += mat[curr][start_node]
    elapsed = time.perf_counter() - t0
    total_cost = assert_valid_tour(instance, tour, total_cost, "NearestNeighbor")
    return tour, total_cost, elapsed


def multi_start_nearest_neighbor(
    instance: TSPInstance,
    max_starts: int = 50,
) -> Tuple[List[int], float, float]:
    """
    Chạy Nearest Neighbor từ nhiều đỉnh xuất phát khác nhau (tối đa `max_starts` đỉnh)
    và giữ lại chu trình có tổng chi phí nhỏ nhất.
    """
    t0 = time.perf_counter()
    n = instance.n
    step = max(1, n // max_starts)
    starts = list(range(0, n, step))[:max_starts]

    best_tour: List[int] = []
    best_cost = float("inf")
    for s in starts:
        tour, cost, _ = nearest_neighbor(instance, start_node=s)
        if cost < best_cost:
            best_cost = cost
            best_tour = tour

    elapsed = time.perf_counter() - t0
    best_cost = assert_valid_tour(instance, best_tour, best_cost, "MultiStart-NN")
    return best_tour, best_cost, elapsed


def cheapest_insertion(
    instance: TSPInstance,
    start_node: int = 0,
) -> Tuple[List[int], float, float]:
    """
    Thuật toán tham lam Chèn rẻ nhất (Cheapest Insertion).
    Nguyên lý:
    1. Khởi tạo chu trình con gồm 2 đỉnh: `start_node` và đỉnh `v` xa nhất (hoặc gần nhất) với nó.
    2. Lặp cho đến khi đủ n đỉnh:
       Ở mỗi bước, tìm đỉnh `k` chưa nằm trong chu trình và cạnh `(i, j)` thuộc chu trình
       sao cho chi phí chèn `delta = d(i, k) + d(k, j) - d(i, j)` là NHỎ NHẤT.
    3. Chèn `k` vào giữa `i` và `j`.
    """
    t0 = time.perf_counter()
    n = instance.n
    mat = instance.dist_matrix

    if n <= 2:
        tour = list(range(n))
        cost = instance.tour_cost(tour)
        return tour, cost, time.perf_counter() - t0

    in_tour = [False] * n
    in_tour[start_node] = True

    # Chọn đỉnh thứ hai gần start_node nhất
    second_node = min(
        (j for j in range(n) if j != start_node),
        key=lambda j: mat[start_node][j],
    )
    in_tour[second_node] = True
    tour = [start_node, second_node]

    # Để tăng tốc từ O(n^3) xuống O(n^2) thực nghiệm:
    # Với mỗi đỉnh k chưa thuộc chu trình, lưu (best_delta[k], best_pos[k])
    INF = float("inf")
    best_delta = [INF] * n
    best_pos = [0] * n

    for k in range(n):
        if not in_tour[k]:
            # Có 2 cạnh trong chu trình 2 đỉnh: (u, v) và (v, u)
            u, v = tour[0], tour[1]
            d1 = mat[u][k] + mat[k][v] - mat[u][v]
            best_delta[k] = d1
            best_pos[k] = 1  # chèn vào vị trí index 1 (giữa u và v)

    for _ in range(n - 2):
        # Tìm đỉnh k chưa thuộc chu trình có best_delta[k] nhỏ nhất
        chosen_k = -1
        min_delta = INF
        for k in range(n):
            if not in_tour[k] and best_delta[k] < min_delta:
                min_delta = best_delta[k]
                chosen_k = k

        pos = best_pos[chosen_k]
        # Đỉnh trước và sau vị trí chèn
        prev_node = tour[pos - 1]
        next_node = tour[pos % len(tour)]

        tour.insert(pos, chosen_k)
        in_tour[chosen_k] = True
        m = len(tour)

        # Cập nhật best_delta cho các đỉnh chưa thuộc chu trình:
        # Cạnh (prev_node, next_node) đã bị thay thế bởi 2 cạnh mới:
        # (prev_node, chosen_k) tại vị trí pos và (chosen_k, next_node) tại vị trí pos + 1
        for k in range(n):
            if in_tour[k]:
                continue
            # Nếu vị trí tốt nhất cũ của k chính là cạnh vừa bị phá vỡ (pos),
            # ta tính lại trên toàn bộ chu trình hiện tại cho đỉnh k đó
            if best_pos[k] == pos:
                bd = INF
                bp = 1
                row_k = mat[k]
                for idx in range(m):
                    u = tour[idx]
                    v = tour[(idx + 1) % m]
                    d = row_k[u] + row_k[v] - mat[u][v]
                    if d < bd:
                        bd = d
                        bp = idx + 1
                best_delta[k] = bd
                best_pos[k] = bp
            else:
                # Nếu best_pos[k] nằm sau vị trí chèn, chỉ số dịch sang phải 1
                if best_pos[k] > pos:
                    best_pos[k] += 1
                # Kiểm tra xem 2 cạnh mới tạo ra có tốt hơn best_delta[k] hiện tại không
                d_new1 = mat[prev_node][k] + mat[k][chosen_k] - mat[prev_node][chosen_k]
                if d_new1 < best_delta[k]:
                    best_delta[k] = d_new1
                    best_pos[k] = pos
                d_new2 = mat[chosen_k][k] + mat[k][next_node] - mat[chosen_k][next_node]
                if d_new2 < best_delta[k]:
                    best_delta[k] = d_new2
                    best_pos[k] = pos + 1

    total_cost = instance.tour_cost(tour)
    elapsed = time.perf_counter() - t0
    total_cost = assert_valid_tour(instance, tour, total_cost, "CheapestInsertion")
    return tour, total_cost, elapsed
