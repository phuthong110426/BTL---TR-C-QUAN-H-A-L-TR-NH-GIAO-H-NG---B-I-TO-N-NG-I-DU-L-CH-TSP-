"""
Mục 3.1.1: Thuật toán chính xác (Exact Algorithms) cho bài toán TSP.
Bao gồm:
1. Quy hoạch động trạng thái bitmask Held–Karp (Bellman 1962; Held & Karp 1962)
   - Độ phức tạp thời gian: O(n^2 * 2^n)
   - Độ phức tạp không gian: O(n * 2^n)
2. Thuật toán Nhánh cận (Branch and Bound) với cận dưới 2-cạnh tối thiểu (2-edge Lower Bound)
   - Hỗ trợ cắt nhánh sớm và giới hạn thời gian thực thi (time_limit).
"""

import time
from array import array
from typing import List, Tuple, Dict, Optional
from .tsp_instance import TSPInstance
from .validator import assert_valid_tour


def solve_held_karp(
    instance: TSPInstance,
    time_limit: float = 600.0,
) -> Tuple[List[int], float, float, bool]:
    """
    Giải chính xác bài toán TSP bằng quy hoạch động Held–Karp O(n^2 * 2^n).
    Cố định đỉnh xuất phát tại 0.
    Trạng thái DP: dp[mask][u] = chi phí đường đi ngắn nhất từ đỉnh 0, đi qua đúng các đỉnh
    được bật bit trong `mask` (bit u-1 ứng với đỉnh u, u in 1..n-1) và kết thúc tại u.

    Tối ưu bộ nhớ:
    - Bảng truy vết `parent` lưu phẳng trong một `bytearray` kích thước 2^(n-1) * n
      (mỗi ô 1 byte vì n <= 127) => n = 23 chỉ tốn ~96 MB.
    - Bảng giá trị `dp` chỉ giữ hai lớp liên tiếp (kích thước tập con s và s+1),
      mỗi trạng thái là một `array('d')` thay vì list số thực Python.

    Trả về:
        (best_tour, best_cost, elapsed_time, is_optimal)
        Nếu hết thời gian: ([], inf, elapsed, False).
    """
    t0 = time.perf_counter()
    n = instance.n
    mat = instance.dist_matrix

    if n <= 1:
        return [0] * n, 0.0, 0.0, True
    if n == 2:
        tour = [0, 1]
        cost = mat[0][1] + mat[1][0]
        return tour, cost, time.perf_counter() - t0, True
    if n > 127:
        raise ValueError("Held-Karp chỉ hỗ trợ n <= 127 (thực tế chỉ khả thi với n <= ~23).")

    m = n - 1
    full_mask = (1 << m) - 1
    INF = float("inf")
    parent = bytearray((full_mask + 1) * n)
    template = array("d", [INF]) * n

    # Lớp cơ sở: tập con một phần tử {u}
    layer: Dict[int, array] = {}
    for u in range(1, n):
        bit = 1 << (u - 1)
        row = array("d", template)
        row[u] = mat[0][u]
        layer[bit] = row
        parent[bit * n + u] = 0

    for _size in range(1, m):
        next_layer: Dict[int, array] = {}
        for mask, dp_mask in layer.items():
            if time.perf_counter() - t0 > time_limit:
                return [], INF, time.perf_counter() - t0, False
            # Danh sách đỉnh thuộc / không thuộc mask
            inside = [u for u in range(1, n) if mask & (1 << (u - 1))]
            outside = [v for v in range(1, n) if not mask & (1 << (v - 1))]
            for v in outside:
                next_mask = mask | (1 << (v - 1))
                row = next_layer.get(next_mask)
                if row is None:
                    row = array("d", template)
                    next_layer[next_mask] = row
                best = row[v]
                best_u = -1
                for u in inside:
                    c = dp_mask[u] + mat[u][v]
                    if c < best:
                        best = c
                        best_u = u
                if best_u >= 0:
                    row[v] = best
                    parent[next_mask * n + v] = best_u
        layer = next_layer  # giải phóng lớp cũ

    # Đóng chu trình: quay về đỉnh 0
    dp_full = layer[full_mask]
    best_cost = INF
    last_node = -1
    for u in range(1, n):
        c = dp_full[u] + mat[u][0]
        if c < best_cost:
            best_cost = c
            last_node = u

    # Truy vết chu trình tối ưu
    tour_rev = []
    curr_mask = full_mask
    curr_node = last_node
    while curr_node != 0:
        tour_rev.append(curr_node)
        prev_node = parent[curr_mask * n + curr_node]
        curr_mask ^= 1 << (curr_node - 1)
        curr_node = prev_node
    tour = [0] + list(reversed(tour_rev))

    elapsed = time.perf_counter() - t0
    best_cost = assert_valid_tour(instance, tour, best_cost, "Held-Karp")
    return tour, best_cost, elapsed, True


def solve_branch_and_bound(
    instance: TSPInstance,
    time_limit: float = 600.0,
    initial_tour: Optional[List[int]] = None,
) -> Tuple[List[int], float, float, bool, int]:
    """
    Giải chính xác bài toán TSP bằng thuật toán Nhánh cận (Branch and Bound).
    - Sử dụng cận dưới 2 cạnh nhỏ nhất trên mỗi đỉnh (1/2 tổng hai cạnh kề ngắn nhất),
      cập nhật gia tăng O(1) khi thêm một cạnh vào đường đi.
    - Khởi tạo cận trên (Upper Bound) bằng chu trình tham lam ban đầu (nếu có) hoặc láng giềng gần nhất.
    - Sắp xếp các nhánh con theo khoảng cách tăng dần để sớm tìm được nghiệm tốt.

    Trả về:
        (best_tour, best_cost, elapsed_time, is_optimal, nodes_explored)
    """
    t0 = time.perf_counter()
    n = instance.n
    mat = instance.dist_matrix

    # Tính 2 cạnh ngắn nhất của mỗi đỉnh để phục vụ cận dưới nhanh O(1)
    min1 = [0.0] * n
    min2 = [0.0] * n
    neighbors_sorted: List[List[int]] = []
    for i in range(n):
        others = sorted((mat[i][j], j) for j in range(n) if j != i)
        min1[i] = others[0][0] if len(others) >= 1 else 0.0
        min2[i] = others[1][0] if len(others) >= 2 else min1[i]
        neighbors_sorted.append([j for _, j in others])

    # Khởi tạo cận trên bằng Nearest Neighbor đơn giản nếu chưa có initial_tour
    if initial_tour is not None:
        best_tour = list(initial_tour)
        best_cost = instance.tour_cost(best_tour)
    else:
        visited_init = [False] * n
        visited_init[0] = True
        best_tour = [0]
        curr = 0
        for _ in range(n - 1):
            nxt = next(j for j in neighbors_sorted[curr] if not visited_init[j])
            visited_init[nxt] = True
            best_tour.append(nxt)
            curr = nxt
        best_cost = instance.tour_cost(best_tour)

    # Cận dưới ban đầu: 0.5 * sum(min1[i] + min2[i])
    initial_lb = 0.5 * sum(min1[i] + min2[i] for i in range(n))

    visited = [False] * n
    visited[0] = True
    current_path = [0]
    nodes_explored = 0
    timed_out = False

    def dfs(curr_node: int, count: int, curr_cost: float, curr_lb: float) -> None:
        nonlocal best_cost, best_tour, nodes_explored, timed_out
        nodes_explored += 1

        if (nodes_explored & 4095) == 0:
            if time.perf_counter() - t0 > time_limit:
                timed_out = True
                return

        if count == n:
            total = curr_cost + mat[curr_node][0]
            if total < best_cost:
                best_cost = total
                best_tour = list(current_path)
            return

        # Duyệt các đỉnh kề theo thứ tự khoảng cách tăng dần
        for nxt in neighbors_sorted[curr_node]:
            if visited[nxt]:
                continue
            edge_w = mat[curr_node][nxt]
            new_cost = curr_cost + edge_w

            # Cập nhật cận dưới khi cố định cạnh (curr_node, nxt).
            # Cận dưới hợp lệ: LB = cost(path) + 0.5 * sum_{w chưa thăm}(min1[w] + min2[w])
            #                       + 0.5 * min1[đỉnh cuối] + 0.5 * min1[0]
            # (mỗi đỉnh chưa thăm còn 2 cạnh, mỗi đầu mút đường đi còn 1 cạnh, mỗi cạnh
            # còn lại có trọng số >= min1 của đầu mút; hai cạnh của một đỉnh >= min1 + min2).
            # - curr_node (khác 0) mất cạnh còn lại cuối cùng: trừ 0.5 * min1[curr_node];
            #   nếu curr_node = 0 ở bước đầu (count == 1): 0 còn 1 cạnh (cạnh đóng chu trình),
            #   nên chỉ trừ 0.5 * min2[0].
            # - nxt chuyển từ "chưa thăm" (2 cạnh) sang "đầu mút" (1 cạnh): trừ 0.5 * min2[nxt].
            delta_lb = edge_w - 0.5 * (
                (min2[curr_node] if count == 1 else min1[curr_node]) + min2[nxt]
            )
            new_lb = curr_lb + delta_lb

            if new_lb < best_cost - 1e-9:
                visited[nxt] = True
                current_path.append(nxt)
                dfs(nxt, count + 1, new_cost, new_lb)
                current_path.pop()
                visited[nxt] = False
                if timed_out:
                    return

    dfs(0, 1, 0.0, initial_lb)
    elapsed = time.perf_counter() - t0
    best_cost = assert_valid_tour(instance, best_tour, best_cost, "Branch-and-Bound")
    return best_tour, best_cost, elapsed, not timed_out, nodes_explored
