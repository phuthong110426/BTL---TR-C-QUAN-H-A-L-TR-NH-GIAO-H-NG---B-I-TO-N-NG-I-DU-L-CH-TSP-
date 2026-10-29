"""
Mục 3.1.3: Tìm kiếm cục bộ (Local Search) và đánh giá gia tăng (Delta Evaluation).
Định nghĩa 3 cấu trúc lân cận:
1. Lân cận 2-opt (đảo ngược đoạn tour[i..j]): xóa 2 cạnh (t[i-1], t[i]) và (t[j], t[j+1]),
   thay bằng (t[i-1], t[j]) và (t[i], t[j+1]). Đánh giá delta trong O(1).
2. Lân cận Swap / 2-exchange (hoán đổi hai đỉnh tại vị trí i và j): đánh giá delta trong O(1).
3. Lân cận Or-opt / Relocate (dịch chuyển một chuỗi k in {1, 2, 3} đỉnh liên tiếp sang vị trí mới):
   đánh giá delta trong O(1).

Hỗ trợ cả 2 chiến lược leo đồi:
- First Improvement (chấp nhận ngay bước cải thiện đầu tiên tìm thấy)
- Best Improvement (duyệt toàn bộ lân cận, chọn bước cải thiện tốt nhất)
"""

import time
from typing import List, Tuple, Optional
from .tsp_instance import TSPInstance
from .validator import assert_valid_tour


def delta_2opt(mat: List[List[float]], tour: List[int], i: int, j: int, n: int) -> float:
    """
    Tính độ biến thiên chi phí (delta = new_cost - old_cost) trong O(1)
    khi đảo ngược đoạn tour[i..j] (với 0 <= i < j < n, và không phải (i=0, j=n-1)).
    """
    if i == 0 and j == n - 1:
        return 0.0
    a = tour[i - 1]
    b = tour[i]
    c = tour[j]
    d = tour[(j + 1) % n]
    return (mat[a][c] + mat[b][d]) - (mat[a][b] + mat[c][d])


def apply_2opt(tour: List[int], i: int, j: int) -> None:
    """Thực hiện phép đảo đoạn tour[i..j] tại chỗ (in-place)."""
    tour[i : j + 1] = reversed(tour[i : j + 1])


def delta_swap(mat: List[List[float]], tour: List[int], i: int, j: int, n: int) -> float:
    """
    Tính độ biến thiên chi phí (delta = new_cost - old_cost) trong O(1)
    khi đổi chỗ hai phần tử tour[i] và tour[j] (0 <= i < j < n).
    Xử lý chính xác cả trường hợp hai vị trí kề nhau (j == i + 1 hoặc i == 0, j == n - 1).
    """
    if i == j:
        return 0.0
    if i > j:
        i, j = j, i

    u = tour[i]
    v = tour[j]
    prev_i = tour[(i - 1) % n]
    next_i = tour[(i + 1) % n]
    prev_j = tour[(j - 1) % n]
    next_j = tour[(j + 1) % n]

    if j == i + 1:
        # Hai đỉnh kề nhau: prev_i - u - v - next_j  -->  prev_i - v - u - next_j
        old_edges = mat[prev_i][u] + mat[u][v] + mat[v][next_j]
        new_edges = mat[prev_i][v] + mat[v][u] + mat[u][next_j]
        return new_edges - old_edges
    elif i == 0 and j == n - 1:
        # Kề nhau qua điểm nối vòng: prev_j - v - u - next_i  -->  prev_j - u - v - next_i
        old_edges = mat[prev_j][v] + mat[v][u] + mat[u][next_i]
        new_edges = mat[prev_j][u] + mat[u][v] + mat[v][next_i]
        return new_edges - old_edges
    else:
        old_edges = mat[prev_i][u] + mat[u][next_i] + mat[prev_j][v] + mat[v][next_j]
        new_edges = mat[prev_i][v] + mat[v][next_i] + mat[prev_j][u] + mat[u][next_j]
        return new_edges - old_edges


def apply_swap(tour: List[int], i: int, j: int) -> None:
    """Hoán đổi hai đỉnh tại vị trí i và j tại chỗ (in-place)."""
    tour[i], tour[j] = tour[j], tour[i]


def hill_climbing_2opt(
    instance: TSPInstance,
    initial_tour: List[int],
    strategy: str = "first",
    max_iters: int = 5000,
    use_candidate_list: bool = False,
) -> Tuple[List[int], float, float, int, List[float]]:
    """
    Tìm kiếm cục bộ Leo đồi (Hill Climbing) với cấu trúc lân cận 2-opt và Delta Evaluation O(1).
    Tham số:
        strategy: 'first' (First Improvement) hoặc 'best' (Best Improvement)
        use_candidate_list: Nếu True, chỉ xét các cặp cạnh trong danh sách láng giềng gần (tăng tốc cho n lớn).
    Trả về:
        (tour, cost, elapsed_time, num_steps, convergence_history)
    """
    t0 = time.perf_counter()
    n = instance.n
    mat = instance.dist_matrix
    tour = list(initial_tour)
    cost = instance.tour_cost(tour)
    history = [cost]
    steps = 0
    eps = -1e-6

    if use_candidate_list and n > 40:
        pos = [0] * n
        for idx, node in enumerate(tour):
            pos[node] = idx
        candidates = instance.candidates
        dont_look = [False] * n

        improved = True
        while improved and steps < max_iters:
            improved = False
            for i in range(n):
                u = tour[i]
                if dont_look[u]:
                    continue
                found_for_u = False
                u_next = tour[(i + 1) % n]
                d_u_unext = mat[u][u_next]
                for v in candidates[u]:
                    if mat[u][v] >= d_u_unext:
                        break
                    j = pos[v]
                    if j == i or j == (i + 1) % n or (j + 1) % n == i:
                        continue
                    idx1, idx2 = (i + 1, j) if i < j else (j + 1, i)
                    if idx1 == 0 and idx2 == n - 1:
                        continue
                    delta = delta_2opt(mat, tour, idx1, idx2, n)
                    if delta < eps:
                        v_next = tour[(idx2 + 1) % n]
                        u_prev = tour[idx1 - 1]
                        apply_2opt(tour, idx1, idx2)
                        for k in range(idx1, idx2 + 1):
                            pos[tour[k]] = k
                        cost += delta
                        steps += 1
                        history.append(cost)
                        dont_look[u_prev] = False
                        dont_look[u] = False
                        dont_look[v] = False
                        dont_look[v_next] = False
                        improved = True
                        found_for_u = True
                        break
                if not found_for_u:
                    dont_look[u] = True
    else:
        is_first = strategy.lower() == "first"
        improved = True
        while improved and steps < max_iters:
            improved = False
            best_delta = 0.0
            best_i, best_j = -1, -1

            for i in range(1, n - 1):
                a = tour[i - 1]
                b = tour[i]
                d_ab = mat[a][b]
                row_a = mat[a]
                row_b = mat[b]
                # Xét cả trường hợp đảo từ 0..j bằng cách cố định chu trình xoay hoặc xét i từ 0
                for j in range(i + 1, n):
                    c = tour[j]
                    d = tour[(j + 1) % n]
                    delta = (row_a[c] + row_b[d]) - (d_ab + mat[c][d])
                    if delta < eps:
                        if is_first:
                            apply_2opt(tour, i, j)
                            cost += delta
                            steps += 1
                            history.append(cost)
                            improved = True
                            break
                        elif delta < best_delta:
                            best_delta = delta
                            best_i, best_j = i, j
                if is_first and improved:
                    break

            if not is_first and best_delta < eps:
                apply_2opt(tour, best_i, best_j)
                cost += best_delta
                steps += 1
                history.append(cost)
                improved = True

    elapsed = time.perf_counter() - t0
    cost = assert_valid_tour(instance, tour, cost, f"HC-2opt-{strategy}")
    return tour, cost, elapsed, steps, history


def hill_climbing_swap(
    instance: TSPInstance,
    initial_tour: List[int],
    strategy: str = "first",
    max_iters: int = 5000,
) -> Tuple[List[int], float, float, int, List[float]]:
    """
    Tìm kiếm cục bộ Leo đồi (Hill Climbing) với cấu trúc lân cận Swap (đổi chỗ 2 đỉnh)
    và Delta Evaluation O(1).
    Tham số:
        strategy: 'first' (First Improvement) hoặc 'best' (Best Improvement)
    """
    t0 = time.perf_counter()
    n = instance.n
    mat = instance.dist_matrix
    tour = list(initial_tour)
    cost = instance.tour_cost(tour)
    history = [cost]
    steps = 0
    eps = -1e-6
    is_first = strategy.lower() == "first"

    improved = True
    while improved and steps < max_iters:
        improved = False
        best_delta = 0.0
        best_i, best_j = -1, -1

        for i in range(n - 1):
            for j in range(i + 1, n):
                delta = delta_swap(mat, tour, i, j, n)
                if delta < eps:
                    if is_first:
                        apply_swap(tour, i, j)
                        cost += delta
                        steps += 1
                        history.append(cost)
                        improved = True
                        break
                    elif delta < best_delta:
                        best_delta = delta
                        best_i, best_j = i, j
            if is_first and improved:
                break

        if not is_first and best_delta < eps:
            apply_swap(tour, best_i, best_j)
            cost += best_delta
            steps += 1
            history.append(cost)
            improved = True

    elapsed = time.perf_counter() - t0
    cost = assert_valid_tour(instance, tour, cost, f"HC-Swap-{strategy}")
    return tour, cost, elapsed, steps, history


def hill_climbing_or_opt(
    instance: TSPInstance,
    initial_tour: List[int],
    strategy: str = "first",
    max_iters: int = 2000,
) -> Tuple[List[int], float, float, int, List[float]]:
    """
    Tìm kiếm cục bộ Leo đồi với cấu trúc lân cận Or-opt (di chuyển chuỗi độ dài seg_len in {1, 2, 3}
    tới vị trí chèn mới) với đánh giá Delta O(1).
    """
    t0 = time.perf_counter()
    n = instance.n
    mat = instance.dist_matrix
    tour = list(initial_tour)
    cost = instance.tour_cost(tour)
    history = [cost]
    steps = 0
    eps = -1e-6
    is_first = strategy.lower() == "first"

    improved = True
    while improved and steps < max_iters:
        improved = False
        best_delta = 0.0
        best_move: Optional[Tuple[int, int, int]] = None  # (start_idx, seg_len, insert_after_idx)

        for seg_len in (1, 2, 3):
            if n <= seg_len + 2:
                continue
            for i in range(n):
                prev_i = tour[(i - 1) % n]
                first_seg = tour[i]
                last_seg = tour[(i + seg_len - 1) % n]
                after_seg = tour[(i + seg_len) % n]

                # Chi phí tiết kiệm khi cắt đoạn [i .. i+seg_len-1] ra khỏi chu trình
                gain_remove = mat[prev_i][first_seg] + mat[last_seg][after_seg] - mat[prev_i][after_seg]

                # Xét vị trí chèn vào sau đỉnh tại vị trí `k`
                for offset in range(seg_len, n - 1):
                    k = (i + offset) % n
                    u = tour[k]
                    v = tour[(k + 1) % n]
                    cost_insert = mat[u][first_seg] + mat[last_seg][v] - mat[u][v]
                    delta = cost_insert - gain_remove
                    if delta < eps:
                        if is_first:
                            best_delta = delta
                            best_move = (i, seg_len, k)
                            improved = True
                            break
                        elif delta < best_delta:
                            best_delta = delta
                            best_move = (i, seg_len, k)
                if is_first and improved:
                    break
            if is_first and improved:
                break

        if best_move is not None and best_delta < eps:
            i, seg_len, k = best_move
            seg_indices = set((i + s) % n for s in range(seg_len))
            segment = [tour[(i + s) % n] for s in range(seg_len)]
            target_node = tour[k]
            remaining = [tour[idx] for idx in range(n) if idx not in seg_indices]
            ins_idx = remaining.index(target_node) + 1
            tour = remaining[:ins_idx] + segment + remaining[ins_idx:]
            cost += best_delta
            steps += 1
            history.append(cost)
            improved = True

    elapsed = time.perf_counter() - t0
    cost = assert_valid_tour(instance, tour, cost, f"HC-OrOpt-{strategy}")
    return tour, cost, elapsed, steps, history
