"""
Mục 3.1.4 & 3.2: Cài đặt 4 Giải thuật Metaheuristic và 1 Thuật toán Lai (Memetic Algorithm)
dành cho nhóm 4 thành viên:

1. Simulated Annealing (SA - Tôi luyện mô phỏng) [Đơn lời giải - Kirkpatrick et al., 1983]
2. Tabu Search (TS - Tìm kiếm Tabu) [Đơn lời giải - Glover, 1986]
3. Genetic Algorithm (GA - Giải thuật di truyền với OX & PMX) [Quần thể - Holland, 1975]
4. Ant Colony Optimization (ACO - Tối ưu đàn kiến MMAS/ACS) [Quần thể - Dorigo & Stützle, 2004]
5. Memetic Algorithm (MA = GA + 2-opt Local Search + Double-Bridge) [Lai - Moscato, 1989]

Mọi thuật toán đều nhận `seed` độc lập để bảo đảm tái lập kết quả 100%,
ghi lại lịch sử hội tụ (convergence curve) theo thời gian và vòng lặp,
và kiểm tra tính hợp lệ qua `assert_valid_tour`.
"""

import math
import random
import time
from typing import List, Tuple, Optional, Dict
from .tsp_instance import TSPInstance
from .constructive import nearest_neighbor
from .local_search import delta_2opt, apply_2opt, delta_swap, apply_swap, hill_climbing_2opt
from .validator import assert_valid_tour


# ==============================================================================
# 1. TÔI LUYỆN MÔ PHỎNG (SIMULATED ANNEALING - SA)
# Tài liệu gốc: Kirkpatrick, S., Gelatt, C. D., & Vecchi, M. P. (1983).
# "Optimization by Simulated Annealing", Science, 220(4598), 671-680.
# ==============================================================================
def simulated_annealing(
    instance: TSPInstance,
    seed: int = 42,
    t0_temp: Optional[float] = None,
    alpha: float = 0.995,
    steps_per_temp: Optional[int] = None,
    t_min: float = 1e-3,
    time_limit: float = 5.0,
    max_iters: int = 10**12,  # chỉ dừng theo time_limit (ngân sách công bằng)
) -> Tuple[List[int], float, float, List[Tuple[float, int, float]]]:
    """
    Giải thuật Tôi luyện mô phỏng (Simulated Annealing - SA) cho TSP.
    - Khởi tạo bằng chu trình Láng giềng gần nhất từ một đỉnh ngẫu nhiên (hoặc hoán vị).
    - Sử dụng lân cận hỗn hợp 2-opt (90%) và Swap (10%) với đánh giá gia tăng O(1).
    - Chấp nhận lời giải xấu hơn (delta > 0) với xác suất Boltzmann: P = exp(-delta / T).
    - Làm nguội theo cấp số nhân: T <- alpha * T sau mỗi `steps_per_temp` bước.
    - Có cơ chế hâm nóng nhẹ (reheating) nếu bị kẹt lâu trước khi hết ngân sách thời gian.
    """
    start_time = time.perf_counter()
    rng = random.Random(seed)
    n = instance.n
    mat = instance.dist_matrix

    # Khởi tạo lời giải bằng Nearest Neighbor từ đỉnh ngẫu nhiên
    init_start = rng.randrange(n)
    curr_tour, curr_cost, _ = nearest_neighbor(instance, start_node=init_start)
    best_tour = list(curr_tour)
    best_cost = curr_cost

    # Tự động ước lượng nhiệt độ đầu T0 dựa trên độ dài trung bình cạnh nếu không truyền vào
    if t0_temp is None:
        t0_temp = max(10.0, curr_cost / (2.0 * n))
    if steps_per_temp is None:
        steps_per_temp = max(20, min(200, 2 * n))

    T = t0_temp
    history: List[Tuple[float, int, float]] = [(0.0, 0, best_cost)]
    iteration = 0
    stagnation = 0

    while iteration < max_iters:
        elapsed = time.perf_counter() - start_time
        if elapsed >= time_limit:
            break

        for _ in range(steps_per_temp):
            iteration += 1
            # Chọn ngẫu nhiên hai vị trí i < j để thực hiện 2-opt (90%) hoặc Swap (10%)
            i = rng.randrange(1, n - 1)
            j = rng.randrange(i + 1, n)

            if rng.random() < 0.9:
                delta = delta_2opt(mat, curr_tour, i, j, n)
                move_type = 0
            else:
                delta = delta_swap(mat, curr_tour, i, j, n)
                move_type = 1

            accept = False
            if delta < -1e-9:
                accept = True
            elif T > 1e-12:
                prob = math.exp(-delta / T)
                if rng.random() < prob:
                    accept = True

            if accept:
                if move_type == 0:
                    apply_2opt(curr_tour, i, j)
                else:
                    apply_swap(curr_tour, i, j)
                curr_cost += delta

                if curr_cost < best_cost - 1e-6:
                    best_cost = curr_cost
                    best_tour = list(curr_tour)
                    stagnation = 0
                else:
                    stagnation += 1
            else:
                stagnation += 1

        T *= alpha
        elapsed = time.perf_counter() - start_time
        history.append((elapsed, iteration, best_cost))

        # Nếu nhiệt độ xuống quá thấp mà vẫn còn thời gian, thực hiện reheating về lời giải tốt nhất
        if T < t_min:
            curr_tour = list(best_tour)
            curr_cost = best_cost
            T = t0_temp * 0.25

    total_time = time.perf_counter() - start_time
    best_cost = assert_valid_tour(instance, best_tour, best_cost, "SA")
    history.append((total_time, iteration, best_cost))
    return best_tour, best_cost, total_time, history


# ==============================================================================
# 2. TÌM KIẾM TABU (TABU SEARCH - TS)
# Tài liệu gốc: Glover, F. (1986). "Future paths for integer programming and
# links to artificial intelligence", Computers & Operations Research, 13(5), 533-549.
# ==============================================================================
def tabu_search(
    instance: TSPInstance,
    seed: int = 42,
    tabu_tenure: Optional[int] = None,
    candidate_sample_size: int = 60,
    time_limit: float = 5.0,
    max_iters: int = 10**12,  # chỉ dừng theo time_limit
) -> Tuple[List[int], float, float, List[Tuple[float, int, float]]]:
    """
    Giải thuật Tìm kiếm Tabu (Tabu Search - TS) cho TSP.
    - Cấu trúc lân cận: 2-opt dựa trên danh sách láng giềng gần (Candidate List) + lấy mẫu.
    - Danh sách Tabu (Tabu List): Lưu thời hạn cấm (iteration_unlock) đối với cặp đỉnh (u, v)
      bị cắt cạnh, ngăn thuật toán quay lại trạng thái vừa thăm.
    - Tiêu chí mong đợi (Aspiration Criterion): Bỏ qua lệnh cấm Tabu nếu phép biến đổi
      tạo ra lời giải tốt hơn kỷ lục toàn cục `best_cost`.
    """
    start_time = time.perf_counter()
    rng = random.Random(seed)
    n = instance.n
    mat = instance.dist_matrix

    if tabu_tenure is None:
        tabu_tenure = max(7, min(40, int(math.sqrt(n) * 2.5)))

    curr_tour, curr_cost, _ = nearest_neighbor(instance, start_node=rng.randrange(n))
    best_tour = list(curr_tour)
    best_cost = curr_cost

    # Tabu table: ánh xạ cặp cạnh (min(u,v), max(u,v)) -> vòng lặp hết hạn cấm
    tabu_dict: Dict[Tuple[int, int], int] = {}
    history: List[Tuple[float, int, float]] = [(0.0, 0, best_cost)]

    # Tạo danh sách các cặp chỉ số (i, j) hợp lệ của phép 2-opt
    all_pairs = [(i, j) for i in range(1, n - 1) for j in range(i + 1, n)]
    total_pairs = len(all_pairs)
    sample_k = min(total_pairs, max(candidate_sample_size, n * 3))

    for it in range(1, max_iters + 1):
        elapsed = time.perf_counter() - start_time
        if elapsed >= time_limit:
            break

        # Duyệt tập ứng viên lân cận 2-opt
        if total_pairs <= sample_k:
            candidates = all_pairs
        else:
            candidates = rng.sample(all_pairs, sample_k)

        best_move_delta = float("inf")
        best_move_ij: Optional[Tuple[int, int]] = None
        best_removed_edge: Optional[Tuple[int, int]] = None

        for i, j in candidates:
            delta = delta_2opt(mat, curr_tour, i, j, n)
            a, b = curr_tour[i - 1], curr_tour[i]
            edge_key = (a, b) if a < b else (b, a)

            is_tabu = tabu_dict.get(edge_key, 0) > it
            # Tiêu chí mong đợi (Aspiration Criterion): cho phép nếu phá kỷ lục best_cost
            if is_tabu and (curr_cost + delta >= best_cost - 1e-6):
                continue

            if delta < best_move_delta:
                best_move_delta = delta
                best_move_ij = (i, j)
                best_removed_edge = edge_key

        if best_move_ij is None:
            # Nếu mọi bước đều bị cấm, chọn ngẫu nhiên 1 bước để thoát
            i, j = rng.choice(all_pairs)
            best_move_delta_rand = delta_2opt(mat, curr_tour, i, j, n)
            apply_2opt(curr_tour, i, j)
            curr_cost += best_move_delta_rand
        else:
            i, j = best_move_ij
            apply_2opt(curr_tour, i, j)
            curr_cost += best_move_delta
            if best_removed_edge is not None:
                # Thêm dao động ngẫu nhiên nhỏ cho tabu tenure (Robust Tabu)
                tenure_jitter = tabu_tenure + rng.randint(-2, 2)
                tabu_dict[best_removed_edge] = it + max(3, tenure_jitter)

        if curr_cost < best_cost - 1e-6:
            best_cost = curr_cost
            best_tour = list(curr_tour)

        if it % 10 == 0 or curr_cost <= best_cost:
            history.append((time.perf_counter() - start_time, it, best_cost))

    total_time = time.perf_counter() - start_time
    best_cost = assert_valid_tour(instance, best_tour, best_cost, "TS")
    history.append((total_time, it if "it" in locals() else 0, best_cost))
    return best_tour, best_cost, total_time, history


# ==============================================================================
# CÁC TOÁN TỬ LAI GHÉP THỨ TỰ CHO GIẢI THUẬT DI TRUYỀN (OX & PMX)
# ==============================================================================
def crossover_ox(p1: List[int], p2: List[int], rng: random.Random) -> List[int]:
    """
    Toán tử lai ghép thứ tự OX (Order Crossover - Davis, 1985).
    Giữ nguyên một đoạn con từ cha `p1`, điền các đỉnh còn lại theo đúng thứ tự xuất hiện ở mẹ `p2`.
    Bảo đảm cá thể con luôn là một hoán vị hợp lệ (không cần sửa chữa).
    """
    n = len(p1)
    a, b = sorted(rng.sample(range(n), 2))
    child = [-1] * n
    in_segment = [False] * n
    for idx in range(a, b + 1):
        val = p1[idx]
        child[idx] = val
        in_segment[val] = True

    pos = (b + 1) % n
    for k in range(n):
        cand = p2[(b + 1 + k) % n]
        if not in_segment[cand]:
            child[pos] = cand
            pos = (pos + 1) % n
    return child


def crossover_pmx(p1: List[int], p2: List[int], rng: random.Random) -> List[int]:
    """
    Toán tử lai ghép ánh xạ một phần PMX (Partially Mapped Crossover - Goldberg & Lingle, 1985).
    """
    n = len(p1)
    a, b = sorted(rng.sample(range(n), 2))
    child = [-1] * n
    mapping: Dict[int, int] = {}
    used = [False] * n

    for idx in range(a, b + 1):
        v1 = p1[idx]
        v2 = p2[idx]
        child[idx] = v1
        used[v1] = True
        mapping[v1] = v2

    for idx in list(range(0, a)) + list(range(b + 1, n)):
        cand = p2[idx]
        while used[cand]:
            cand = mapping[cand]
        child[idx] = cand
        used[cand] = True
    return child


# ==============================================================================
# 3. GIẢI THUẬT DI TRUYỀN (GENETIC ALGORITHM - GA)
# Tài liệu gốc: Holland, J. H. (1975). "Adaptation in Natural and Artificial Systems";
# Oliver, I. M., Smith, D. J., & Holland, J. R. (1987) cho OX/PMX trên TSP.
# ==============================================================================
def genetic_algorithm(
    instance: TSPInstance,
    seed: int = 42,
    pop_size: int = 60,
    crossover_rate: float = 0.85,
    mutation_rate: float = 0.20,
    elite_size: int = 4,
    crossover_type: str = "OX",
    time_limit: float = 5.0,
    max_generations: int = 10**12,  # chỉ dừng theo time_limit
) -> Tuple[List[int], float, float, List[Tuple[float, int, float]]]:
    """
    Giải thuật Di truyền (Genetic Algorithm - GA) cho TSP:
    - Mã hóa cá thể: Hoán vị trực tiếp của n đỉnh [0, 1, ..., n-1].
    - Khởi tạo quần thể: Kết hợp một số cá thể Nearest Neighbor từ các đỉnh ngẫu nhiên (15%)
      và các cá thể hoán vị ngẫu nhiên (85%) để duy trì tính đa dạng quần thể.
    - Chọn lọc: Đấu loại k=3 (Tournament Selection).
    - Lai ghép: Order Crossover (OX) hoặc Partially Mapped Crossover (PMX).
    - Đột biến: Đảo đoạn (Inversion / 2-opt ngẫu nhiên) kết hợp đổi chỗ (Swap).
    - Thay thế: Giữ lại `elite_size` cá thể ưu tú nhất (Elitism).
    """
    start_time = time.perf_counter()
    rng = random.Random(seed)
    n = instance.n

    population: List[List[int]] = []
    fitness: List[float] = []

    # Khởi tạo quần thể ban đầu
    num_seeded = max(1, min(pop_size // 6, n))
    seeded_starts = rng.sample(range(n), num_seeded)
    for s in seeded_starts:
        t_nn, c_nn, _ = nearest_neighbor(instance, start_node=s)
        # Nhiễu nhẹ để tạo đa dạng
        if len(population) > 0 and n >= 6:
            i, j = sorted(rng.sample(range(1, n), 2))
            apply_2opt(t_nn, i, j)
            c_nn = instance.tour_cost(t_nn)
        population.append(t_nn)
        fitness.append(c_nn)

    base_nodes = list(range(n))
    while len(population) < pop_size:
        perm = list(base_nodes)
        rng.shuffle(perm)
        population.append(perm)
        fitness.append(instance.tour_cost(perm))

    best_idx = min(range(pop_size), key=lambda k: fitness[k])
    best_tour = list(population[best_idx])
    best_cost = fitness[best_idx]
    history: List[Tuple[float, int, float]] = [(0.0, 0, best_cost)]

    use_ox = crossover_type.upper() != "PMX"

    def tournament_select() -> List[int]:
        i1, i2, i3 = rng.randrange(pop_size), rng.randrange(pop_size), rng.randrange(pop_size)
        best_i = i1
        if fitness[i2] < fitness[best_i]:
            best_i = i2
        if fitness[i3] < fitness[best_i]:
            best_i = i3
        return population[best_i]

    gen = 0
    for gen in range(1, max_generations + 1):
        elapsed = time.perf_counter() - start_time
        if elapsed >= time_limit:
            break

        # Sắp xếp quần thể để lấy nhóm Elitism
        ranked_indices = sorted(range(pop_size), key=lambda k: fitness[k])
        new_pop: List[List[int]] = [list(population[idx]) for idx in ranked_indices[:elite_size]]
        new_fit: List[float] = [fitness[idx] for idx in ranked_indices[:elite_size]]

        while len(new_pop) < pop_size:
            p1 = tournament_select()
            p2 = tournament_select()
            if rng.random() < crossover_rate:
                child = crossover_ox(p1, p2, rng) if use_ox else crossover_pmx(p1, p2, rng)
            else:
                child = list(p1)

            # Đột biến đảo đoạn (Inversion) hoặc đổi chỗ (Swap)
            if rng.random() < mutation_rate:
                i, j = sorted(rng.sample(range(n), 2))
                if rng.random() < 0.8:
                    apply_2opt(child, i, j)
                else:
                    apply_swap(child, i, j)

            c_cost = instance.tour_cost(child)
            new_pop.append(child)
            new_fit.append(c_cost)

            if c_cost < best_cost - 1e-6:
                best_cost = c_cost
                best_tour = list(child)

        population = new_pop
        fitness = new_fit
        history.append((time.perf_counter() - start_time, gen, best_cost))

    total_time = time.perf_counter() - start_time
    best_cost = assert_valid_tour(instance, best_tour, best_cost, "GA")
    history.append((total_time, gen, best_cost))
    return best_tour, best_cost, total_time, history


# ==============================================================================
# 4. TỐI ƯU ĐÀN KIẾN (ANT COLONY OPTIMIZATION - ACO / MMAS)
# Tài liệu gốc: Dorigo, M. (1992); Stützle, T., & Hoos, H. H. (2000) "MAX-MIN Ant System";
# Dorigo, M., & Stützle, T. (2004). Ant Colony Optimization, MIT Press.
# ==============================================================================
def ant_colony_optimization(
    instance: TSPInstance,
    seed: int = 42,
    num_ants: int = 25,
    alpha: float = 1.0,
    beta: float = 3.0,
    rho: float = 0.15,
    q0: float = 0.5,
    time_limit: float = 5.0,
    max_iters: int = 10**12,  # chỉ dừng theo time_limit
) -> Tuple[List[int], float, float, List[Tuple[float, int, float]]]:
    """
    Giải thuật Tối ưu Đàn kiến (ACO - kết hợp cơ chế ACS pseudorandom proportional rule `q0`
    và giới hạn mùi MAX-MIN Ant System):
    - Mỗi con kiến xây dựng một chu trình hợp lệ dựa trên vết mùi `tau[i][j]^alpha` và
      thông tin heuristic `eta[i][j]^beta` (với `eta[i][j] = 1 / d(i, j)`).
    - Tối ưu hóa tốc độ bằng Danh sách láng giềng gần (Candidate List).
    - Sau mỗi thế hệ, vết mùi bay hơi theo hệ số `rho` và kiến tốt nhất vòng lặp / toàn cục
      được bồi đắp thêm mùi `Delta_tau = 1 / L_best`.
    """
    start_time = time.perf_counter()
    rng = random.Random(seed)
    n = instance.n
    mat = instance.dist_matrix
    candidates = instance.candidates

    # Tạo chu trình tham lam ban đầu để định chuẩn mức mùi khởi tạo tau_0
    init_tour, init_cost, _ = nearest_neighbor(instance, start_node=rng.randrange(n))
    best_tour = list(init_tour)
    best_cost = init_cost

    tau_max = 1.0 / (rho * best_cost)
    tau_min = tau_max / (2.0 * n)
    tau = [[tau_max] * n for _ in range(n)]

    # Tính trước eta[i][j]^beta
    eta_beta = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                d = max(1e-4, mat[i][j])
                eta_beta[i][j] = (1.0 / d) ** beta

    history: List[Tuple[float, int, float]] = [(0.0, 0, best_cost)]

    it = 0
    for it in range(1, max_iters + 1):
        elapsed = time.perf_counter() - start_time
        if elapsed >= time_limit:
            break

        iter_best_tour: List[int] = []
        iter_best_cost = float("inf")

        for _ant in range(num_ants):
            start_node = rng.randrange(n)
            visited = [False] * n
            visited[start_node] = True
            tour = [start_node]
            curr = start_node
            cost = 0.0

            for _step in range(n - 1):
                # Ưu tiên xét các đỉnh chưa thăm trong Candidate List của `curr`
                avail = [v for v in candidates[curr] if not visited[v]]
                if not avail:
                    avail = [v for v in range(n) if not visited[v]]

                tau_row = tau[curr]
                eta_row = eta_beta[curr]

                if rng.random() < q0:
                    # Khai thác (Exploitation): chọn đỉnh có (tau^alpha * eta^beta) lớn nhất
                    nxt = max(avail, key=lambda v: (tau_row[v] ** alpha) * eta_row[v])
                else:
                    # Khám phá có hướng (Biased Exploration): bánh xe Roulette
                    weights = []
                    total_w = 0.0
                    for v in avail:
                        w = (tau_row[v] ** alpha) * eta_row[v]
                        weights.append(w)
                        total_w += w
                    if total_w <= 0.0:
                        nxt = rng.choice(avail)
                    else:
                        r = rng.random() * total_w
                        acc = 0.0
                        nxt = avail[-1]
                        for v, w in zip(avail, weights):
                            acc += w
                            if acc >= r:
                                nxt = v
                                break

                visited[nxt] = True
                tour.append(nxt)
                cost += mat[curr][nxt]
                curr = nxt

            cost += mat[curr][start_node]
            if cost < iter_best_cost:
                iter_best_cost = cost
                iter_best_tour = tour

        # Làm mịn chu trình của kiến tốt nhất vòng lặp bằng vài bước 2-opt nhanh
        iter_best_tour, iter_best_cost, _, _, _ = hill_climbing_2opt(
            instance, iter_best_tour, strategy="first", max_iters=30
        )

        if iter_best_cost < best_cost - 1e-6:
            best_cost = iter_best_cost
            best_tour = list(iter_best_tour)
            tau_max = 1.0 / (rho * best_cost)
            tau_min = tau_max / (2.0 * n)

        # Bay hơi vết mùi trên toàn bộ các cạnh
        evap = 1.0 - rho
        for i in range(n):
            row_t = tau[i]
            for j in range(n):
                val = row_t[j] * evap
                row_t[j] = tau_min if val < tau_min else val

        # Bồi đắp mùi từ kiến tốt nhất toàn cục (50% số vòng) hoặc kiến tốt nhất thế hệ
        deposit_tour = best_tour if (it % 2 == 0) else iter_best_tour
        deposit_cost = best_cost if (it % 2 == 0) else iter_best_cost
        delta_tau = 1.0 / deposit_cost
        for k in range(n):
            u = deposit_tour[k]
            v = deposit_tour[(k + 1) % n]
            new_val = min(tau_max, tau[u][v] + delta_tau)
            tau[u][v] = new_val
            tau[v][u] = new_val

        history.append((time.perf_counter() - start_time, it, best_cost))

    total_time = time.perf_counter() - start_time
    best_cost = assert_valid_tour(instance, best_tour, best_cost, "ACO")
    history.append((total_time, it, best_cost))
    return best_tour, best_cost, total_time, history


# ==============================================================================
# 5. THUẬT TOÁN LAI MEMETIC (MEMETIC ALGORITHM: GA + 2-OPT + DOUBLE-BRIDGE)
# Tài liệu gốc: Moscato, P. (1989). "On Evolution, Search, Optimization, Genetic
# Algorithms and Martial Arts: Towards Memetic Algorithms".
# Yêu cầu riêng cho nhóm 4 thành viên (Mục 2.2).
# ==============================================================================
def double_bridge_move(tour: List[int], rng: random.Random) -> List[int]:
    """
    Phép nhiễu 4-opt Double-Bridge (Lin & Kernighan; Martin, Otto & Felten, 1991).
    Chia chu trình thành 4 đoạn A, B, C, D và nối lại theo thứ tự A - D - C - B.
    Không thể bị hoàn tác bởi các bước 2-opt đơn lẻ, giúp thoát cực trị cục bộ rất hiệu quả.
    """
    n = len(tour)
    if n < 8:
        res = list(tour)
        i, j = sorted(rng.sample(range(n), 2))
        apply_2opt(res, i, j)
        return res
    cuts = sorted(rng.sample(range(1, n), 3))
    p1, p2, p3 = cuts[0], cuts[1], cuts[2]
    return tour[:p1] + tour[p3:] + tour[p2:p3] + tour[p1:p2]


def memetic_algorithm(
    instance: TSPInstance,
    seed: int = 42,
    pop_size: int = 30,
    crossover_rate: float = 0.90,
    mutation_rate: float = 0.25,
    ls_max_steps: int = 150,
    time_limit: float = 5.0,
    max_generations: int = 10**12,  # chỉ dừng theo time_limit
) -> Tuple[List[int], float, float, List[Tuple[float, int, float]]]:
    """
    Giải thuật Memetic (Thuật toán Di truyền Lai ghép với Tìm kiếm cục bộ 2-opt):
    - Kết hợp khả năng khám phá vùng không gian rộng của GA (lai ghép thứ tự OX)
      với khả năng khai thác sâu của tìm kiếm cục bộ 2-opt (First Improvement + Candidate List).
    - Áp dụng toán tử nhiễu Double-Bridge (4-opt) để chống hội tụ sớm khi các cá thể trùng lặp.
    """
    start_time = time.perf_counter()
    rng = random.Random(seed)
    n = instance.n

    population: List[List[int]] = []
    fitness: List[float] = []

    # Khởi tạo quần thể đã qua tinh chỉnh 2-opt cục bộ
    for idx in range(pop_size):
        if idx < min(pop_size // 3, n):
            t_init, _, _ = nearest_neighbor(instance, start_node=(idx * 7 + seed) % n)
        else:
            t_init = list(range(n))
            rng.shuffle(t_init)
        t_opt, c_opt, _, _, _ = hill_climbing_2opt(
            instance, t_init, strategy="first", max_iters=ls_max_steps, use_candidate_list=(n > 60)
        )
        population.append(t_opt)
        fitness.append(c_opt)
        if time.perf_counter() - start_time >= time_limit * 0.4:
            break

    pop_size = len(population)
    best_idx = min(range(pop_size), key=lambda k: fitness[k])
    best_tour = list(population[best_idx])
    best_cost = fitness[best_idx]
    history: List[Tuple[float, int, float]] = [(time.perf_counter() - start_time, 0, best_cost)]

    gen = 0
    for gen in range(1, max_generations + 1):
        elapsed = time.perf_counter() - start_time
        if elapsed >= time_limit:
            break

        # Mỗi thế hệ tạo pop_size // 2 cá thể con được tối ưu cục bộ (Steady-State / Generational)
        num_offspring = max(4, pop_size // 2)
        for _ in range(num_offspring):
            if time.perf_counter() - start_time >= time_limit:
                break
            # Chọn 2 cha mẹ bằng đấu loại
            i1, i2 = rng.randrange(pop_size), rng.randrange(pop_size)
            p1 = population[i1 if fitness[i1] < fitness[i2] else i2]
            j1, j2 = rng.randrange(pop_size), rng.randrange(pop_size)
            p2 = population[j1 if fitness[j1] < fitness[j2] else j2]

            if rng.random() < crossover_rate:
                child = crossover_ox(p1, p2, rng)
            else:
                child = list(p1)

            if rng.random() < mutation_rate:
                child = double_bridge_move(child, rng)

            # Pha học cục bộ (Lamarckian Local Search 2-opt)
            child, c_cost, _, _, _ = hill_climbing_2opt(
                instance, child, strategy="first", max_iters=ls_max_steps, use_candidate_list=(n > 60)
            )

            if c_cost < best_cost - 1e-6:
                best_cost = c_cost
                best_tour = list(child)

            # Thay thế cá thể xấu nhất trong quần thể nếu cá thể con tốt hơn và chưa trùng chi phí
            worst_idx = max(range(pop_size), key=lambda k: fitness[k])
            is_duplicate = any(abs(f - c_cost) < 1e-5 for f in fitness)
            if c_cost < fitness[worst_idx] and not is_duplicate:
                population[worst_idx] = child
                fitness[worst_idx] = c_cost
            elif is_duplicate and rng.random() < 0.3:
                # Đa dạng hóa cá thể xấu nhất bằng Double-Bridge + 2-opt
                pert = double_bridge_move(best_tour, rng)
                pert, p_cost, _, _, _ = hill_climbing_2opt(
                    instance, pert, strategy="first", max_iters=ls_max_steps, use_candidate_list=(n > 60)
                )
                population[worst_idx] = pert
                fitness[worst_idx] = p_cost
                if p_cost < best_cost - 1e-6:
                    best_cost = p_cost
                    best_tour = list(pert)

        history.append((time.perf_counter() - start_time, gen, best_cost))

    total_time = time.perf_counter() - start_time
    best_cost = assert_valid_tour(instance, best_tour, best_cost, "Memetic")
    history.append((total_time, gen, best_cost))
    return best_tour, best_cost, total_time, history
