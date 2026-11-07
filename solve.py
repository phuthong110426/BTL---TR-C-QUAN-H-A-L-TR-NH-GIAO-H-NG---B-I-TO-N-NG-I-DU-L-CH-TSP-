"""
Chương trình dòng lệnh (CLI) chạy thuật toán giải bài toán TSP trên một thể hiện bất kỳ
theo đúng yêu cầu tại Mục 6.3 (trang 32) và phục vụ 4 kịch bản Demo bảo vệ tại Mục 7.2 (trang 35).

Cú pháp sử dụng:
    python solve.py --instance <tệp_hoặc_tên> --algo <thuật_toán> [--seed <seed>] [--budget <giây>] [--out <tệp_ra.sol>] [--all-seeds]

Danh sách mã thuật toán (--algo):
    - EXACT / EXACT_HK : Quy hoạch động Held-Karp O(n^2 * 2^n)
    - EXACT_BB         : Nhánh cận (Branch and Bound)
    - GREEDY / NN      : Tham lam Láng giềng gần nhất (Nearest Neighbor)
    - CI               : Tham lam Chèn rẻ nhất (Cheapest Insertion)
    - HC_FI            : Leo đồi 2-opt First Improvement (Delta O(1))
    - HC_BI            : Leo đồi 2-opt Best Improvement (Delta O(1))
    - SA               : Tôi luyện mô phỏng (Simulated Annealing)
    - TS               : Tìm kiếm Tabu (Tabu Search)
    - GA               : Giải thuật di truyền (Genetic Algorithm - OX)
    - ACO              : Tối ưu đàn kiến (Ant Colony Optimization - MMAS)
    - MEMETIC          : Thuật toán Lai (Memetic Algorithm = GA + 2-opt + Double-Bridge)

Các ví dụ chạy trực tiếp cho 4 bước Demo Mục 7.2:
    1. Kiểm tra ví dụ nhỏ:
       python kiemtra.py data/vidu/vidu.txt data/vidu/vidu.sol
    2. Giải chính xác ví dụ nhỏ (ra đúng tối ưu = 31):
       python solve.py --instance data/vidu/vidu.txt --algo EXACT --out results/solutions/vidu_EXACT.sol
    3. Chạy 1 metaheuristic trên thể hiện chuẩn với seed cho trước & hiển thị diễn biến hội tụ:
       python solve.py --instance data/chuan/berlin52.tsp --algo MEMETIC --seed 1001 --budget 0.35
    4. Tái lập 1 dòng kết quả trong báo cáo (theo seed đơn lẻ hoặc toàn bộ 10 seeds 1001..1010):
       python solve.py --instance kroA100 --algo MEMETIC --seed 1001
       python solve.py --instance berlin52 --algo MEMETIC --all-seeds
"""

import argparse
import csv
import os
import statistics
import sys
from typing import Dict, Optional, List, Tuple

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.tsp_instance import TSPInstance
from src.validator import validate_tour
from src.exact_solver import solve_held_karp, solve_branch_and_bound
from src.constructive import nearest_neighbor, cheapest_insertion
from src.local_search import hill_climbing_2opt, hill_climbing_swap, hill_climbing_or_opt
from src.metaheuristics import (
    simulated_annealing,
    tabu_search,
    genetic_algorithm,
    ant_colony_optimization,
    memetic_algorithm,
)
from run_experiments import get_budget_seconds, SEEDS

KNOWN_BKS: Dict[str, float] = {
    "vidu": 31.0,
    "syn_10": 1687.0,
    "syn_12": 1269.0,
    "syn_15": 966.0,
    "syn_16": 1841.0,
    "syn_18": 1013.0,
    "syn_40": 4993.0,
    "eil51": 426.0,
    "berlin52": 7542.0,
    "st70": 675.0,
    "eil76": 538.0,
    "kroA100": 21282.0,
    "syn_120": 6081.0,
}

ALGO_CANONICAL: Dict[str, str] = {
    "EXACT": "EXACT_HK",
    "EXACT_HK": "EXACT_HK",
    "HK": "EXACT_HK",
    "HELD_KARP": "EXACT_HK",
    "EXACT_BB": "EXACT_BB",
    "BB": "EXACT_BB",
    "GREEDY": "NN",
    "NN": "NN",
    "CI": "CI",
    "HC_FI": "HC_FI",
    "2OPT_FI": "HC_FI",
    "HC_BI": "HC_BI",
    "2OPT_BI": "HC_BI",
    "SWAP_FI": "SWAP_FI",
    "OROPT_FI": "OROPT_FI",
    "SA": "SA",
    "TS": "TS",
    "GA": "GA",
    "ACO": "ACO",
    "MEMETIC": "Memetic",
    "MA": "Memetic",
}


def resolve_instance_path(instance_arg: str) -> str:
    """Tìm đường dẫn tệp dữ liệu từ tên thể hiện hoặc đường dẫn tương đối."""
    if os.path.exists(instance_arg):
        return instance_arg
    candidates = [instance_arg]
    if not instance_arg.endswith((".tsp", ".txt")):
        candidates.extend([f"{instance_arg}.tsp", f"{instance_arg}.txt"])
    search_dirs = [
        ROOT_DIR,
        os.path.join(ROOT_DIR, "data", "vidu"),
        os.path.join(ROOT_DIR, "data", "chuan"),
        os.path.join(ROOT_DIR, "data", "tusinh"),
        os.path.join(ROOT_DIR, "data", "tsplib"),
        os.path.join(ROOT_DIR, "data", "synthetic"),
    ]
    for d in search_dirs:
        for cand in candidates:
            p = os.path.join(d, cand)
            if os.path.exists(p):
                return p
    raise FileNotFoundError(f"Không tìm thấy tệp dữ liệu cho thể hiện: '{instance_arg}'")


def print_convergence_evolution(history: List, budget: float) -> None:
    """In bảng diễn biến giá trị tốt nhất (convergence progress) theo Mục 7.2(3)."""
    if not history:
        return
    print("\n  [DIEN BIEN GIA TRI TOT NHAT THEO QUA TRINH TIM KIEM]")
    print(f"  {'Moc tien trinh / Thoi gian':<28} | {'Chi phi tot nhat (Best)':<22} | {'Cai thien so voi ban dau':<20}")
    print("  " + "-" * 76)

    # Chuẩn hóa history về danh sách (step_idx, time_sec_or_None, cost_val)
    normalized: List[Tuple[int, Optional[float], float]] = []
    for idx, item in enumerate(history):
        if isinstance(item, (tuple, list)) and len(item) >= 3:
            normalized.append((int(item[1]), float(item[0]), float(item[2])))
        elif isinstance(item, (tuple, list)) and len(item) == 2:
            normalized.append((idx, float(item[0]), float(item[1])))
        else:
            normalized.append((idx, None, float(item)))

    init_val = normalized[0][2]

    # Trích xuất các mốc thay đổi giá trị hoặc mốc đầu/cuối
    milestones: List[Tuple[int, Optional[float], float]] = [normalized[0]]
    last_val = normalized[0][2]
    for step_idx, t_sec, val in normalized[1:]:
        if val < last_val:
            milestones.append((step_idx, t_sec, val))
            last_val = val
    if milestones[-1] != normalized[-1]:
        milestones.append(normalized[-1])

    if len(milestones) > 10:
        indices = [0] + [int(i * (len(milestones) - 1) / 8) for i in range(1, 8)] + [len(milestones) - 1]
        seen = set()
        filtered = []
        for idx_m in indices:
            if idx_m not in seen:
                seen.add(idx_m)
                filtered.append(milestones[idx_m])
        milestones = filtered

    for m_idx, (step_idx, t_sec, val) in enumerate(milestones):
        impr = ((init_val - val) / init_val * 100.0) if init_val > 0 else 0.0
        t_str = f" ({t_sec:.4f}s)" if t_sec is not None else ""
        if m_idx == 0:
            label = f"Khoi tao{t_str}"
        elif m_idx == len(milestones) - 1:
            label = f"Ket thuc{t_str}"
        else:
            label = f"Vong #{step_idx}{t_str}"
        print(f"  {label:<28} | {val:<22.0f} | -{impr:.2f}%")


def lookup_recorded_run(inst_name: str, alg_name: str, seed: int) -> Optional[Dict[str, str]]:
    """Tra cứu dòng kết quả đã ghi trong results/raw_runs.csv để đối chiếu tái lập."""
    raw_csv = os.path.join(ROOT_DIR, "results", "raw_runs.csv")
    if not os.path.exists(raw_csv):
        return None
    with open(raw_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (
                row.get("instance", "").lower() == inst_name.lower()
                and row.get("algorithm", "").lower() == alg_name.lower()
                and int(row.get("seed", -1)) == seed
            ):
                return row
    return None


def lookup_recorded_summary(inst_name: str, alg_name: str) -> Optional[Dict[str, str]]:
    """Tra cứu dòng tổng hợp trong results/summary_results.csv."""
    sum_csv = os.path.join(ROOT_DIR, "results", "summary_results.csv")
    if not os.path.exists(sum_csv):
        return None
    with open(sum_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (
                row.get("instance", "").lower() == inst_name.lower()
                and row.get("algorithm", "").lower() == alg_name.lower()
            ):
                return row
    return None


def run_single(
    inst: TSPInstance,
    alg_canonical: str,
    seed: int,
    budget: float,
) -> Tuple[List[int], float, float, List[float]]:
    """Thực thi 1 thuật toán và trả về (tour, cost, elapsed_time, convergence_history)."""
    if alg_canonical == "EXACT_HK":
        tour, cost, elapsed, _ = solve_held_karp(inst, time_limit=max(budget, 60.0))
        return tour, cost, elapsed, [cost]
    elif alg_canonical == "EXACT_BB":
        init_t, init_c, _ = nearest_neighbor(inst, 0)
        tour, cost, elapsed, _, _ = solve_branch_and_bound(inst, time_limit=max(budget, 15.0), initial_tour=init_t)
        return tour, cost, elapsed, [init_c, cost]
    elif alg_canonical == "NN":
        tour, cost, elapsed = nearest_neighbor(inst, 0)
        return tour, cost, elapsed, [cost]
    elif alg_canonical == "CI":
        tour, cost, elapsed = cheapest_insertion(inst, 0)
        return tour, cost, elapsed, [cost]
    elif alg_canonical == "HC_FI":
        init_t, _, _ = nearest_neighbor(inst, 0)
        tour, cost, elapsed, _, hist = hill_climbing_2opt(
            inst, init_t, strategy="first", use_candidate_list=(inst.n >= 200)
        )
        return tour, cost, elapsed, hist
    elif alg_canonical == "HC_BI":
        init_t, _, _ = nearest_neighbor(inst, 0)
        tour, cost, elapsed, _, hist = hill_climbing_2opt(inst, init_t, strategy="best")
        return tour, cost, elapsed, hist
    elif alg_canonical == "SWAP_FI":
        init_t, _, _ = nearest_neighbor(inst, 0)
        tour, cost, elapsed, _, hist = hill_climbing_swap(inst, init_t, strategy="first")
        return tour, cost, elapsed, hist
    elif alg_canonical == "OROPT_FI":
        init_t, _, _ = nearest_neighbor(inst, 0)
        tour, cost, elapsed, _, hist = hill_climbing_or_opt(inst, init_t, strategy="first")
        return tour, cost, elapsed, hist
    elif alg_canonical == "SA":
        return simulated_annealing(inst, seed=seed, time_limit=budget)
    elif alg_canonical == "TS":
        return tabu_search(inst, seed=seed, time_limit=budget)
    elif alg_canonical == "GA":
        return genetic_algorithm(inst, seed=seed, time_limit=budget)
    elif alg_canonical == "ACO":
        return ant_colony_optimization(inst, seed=seed, time_limit=budget)
    elif alg_canonical == "Memetic":
        return memetic_algorithm(inst, seed=seed, time_limit=budget)
    else:
        raise ValueError(f"Thuật toán không hợp lệ: {alg_canonical}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Chuong trinh CLI chay thuat toan giai bai toan TSP (De 1 - Muc 6.3 & 7.2)"
    )
    parser.add_argument(
        "--instance", "--input", "-i", dest="instance", type=str, required=True,
        help="Duong dan tep hoac ten the hien (vd: data/vidu/vidu.txt, berlin52, kroA100, syn_15)"
    )
    parser.add_argument(
        "--algo", "-a", type=str, default="MEMETIC",
        help="Thuat toan: EXACT, EXACT_HK, EXACT_BB, NN, CI, HC_FI, HC_BI, SA, TS, GA, ACO, MEMETIC"
    )
    parser.add_argument(
        "--seed", "-s", type=int, default=1001,
        help="Hat giong ngau nhien (mac dinh: 1001)"
    )
    parser.add_argument(
        "--budget", "--time-limit", "-b", dest="budget", type=float, default=None,
        help="Ngan sach thoi gian (giay). Neu bo trong, dung ngan sach chuan cua thuc nghiem theo n."
    )
    parser.add_argument(
        "--out", "--output", "-o", dest="out", type=str, default=None,
        help="Duong dan tep loi giai (.sol) dau ra"
    )
    parser.add_argument(
        "--all-seeds", action="store_true",
        help="Chay toan bo 10 seeds (1001..1010) de tai lap 1 dong trong bang ket qua tong hop"
    )

    args = parser.parse_args()

    in_path = resolve_instance_path(args.instance)
    inst = TSPInstance.from_file(in_path)
    if inst.bks is None and inst.name in KNOWN_BKS:
        inst.bks = KNOWN_BKS[inst.name]

    algo_key = args.algo.strip().upper()
    if algo_key not in ALGO_CANONICAL:
        print(f"Loi: Thuat toan '{args.algo}' khong duoc ho tro. Chon trong: {list(ALGO_CANONICAL.keys())}")
        sys.exit(1)
    alg_canonical = ALGO_CANONICAL[algo_key]

    budget = args.budget if args.budget is not None else get_budget_seconds(inst.n)

    print("=" * 76)
    print(f"CHAY THUAT TOAN TSP | The hien: {inst.name} (n = {inst.n}) | Thuat toan: {alg_canonical}")
    if inst.bks is not None:
        print(f"Gia tri toi uu / BKS: {inst.bks:.0f} | Ngan sach thoi gian: {budget:.2f}s | Seed: {args.seed}")
    else:
        print(f"Ngan sach thoi gian : {budget:.2f}s | Seed: {args.seed}")
    print("=" * 76)

    if args.all_seeds and alg_canonical in ("SA", "TS", "GA", "ACO", "Memetic"):
        print(f"\nDang chay tai lap 10 lan doc lap voi bo SEEDS = {SEEDS}...")
        costs = []
        times = []
        best_overall_tour = None
        best_overall_cost = float("inf")
        best_seed = SEEDS[0]

        for idx, s in enumerate(SEEDS, start=1):
            t_run, c_run, el_run, _ = run_single(inst, alg_canonical, s, budget)
            valid, ver_c, msg = validate_tour(inst, t_run, c_run)
            if not valid:
                raise RuntimeError(f"Loi giai khong hop le tai seed {s}: {msg}")
            costs.append(ver_c)
            times.append(el_run)
            if ver_c < best_overall_cost:
                best_overall_cost = ver_c
                best_overall_tour = t_run
                best_seed = s
            gap_s = ((ver_c - inst.bks) / inst.bks * 100.0) if inst.bks else 0.0
            print(f"  - Run #{idx:2d} (seed={s}): Cost = {ver_c:8.0f} | Gap = {gap_s:6.3f}% | Time = {el_run:.4f}s | HOP LE")

        best_c = min(costs)
        mean_c = statistics.mean(costs)
        std_c = statistics.stdev(costs)
        mean_t = statistics.mean(times)
        gap_b = ((best_c - inst.bks) / inst.bks * 100.0) if inst.bks else 0.0
        gap_a = ((mean_c - inst.bks) / inst.bks * 100.0) if inst.bks else 0.0

        print("-" * 76)
        print("TONG HOP 10 SEEDS VUA CHAY:")
        print(
            f"  Best = {best_c:.0f} (Gap_b = {gap_b:.3f}%) | Avg = {mean_c:.1f} (Gap_a = {gap_a:.3f}%) | "
            f"Std = {std_c:.2f} | T_tb = {mean_t:.4f}s"
        )
        rec_sum = lookup_recorded_summary(inst.name, alg_canonical)
        if rec_sum:
            print("DOI CHIEU DONG GHI TRONG BAO CAO (results/summary_results.csv):")
            print(
                f"  Best = {float(rec_sum['best_cost']):.0f} (Gap_b = {float(rec_sum['best_gap_pct']):.3f}%) | "
                f"Avg = {float(rec_sum['mean_cost']):.1f} (Gap_a = {float(rec_sum['mean_gap_pct']):.3f}%) | "
                f"Std = {float(rec_sum['std_cost']):.2f} | T_tb = {float(rec_sum['mean_time_sec']):.4f}s"
            )
        out_path = args.out or os.path.join(
            ROOT_DIR, "results", "solutions", f"{inst.name}_{alg_canonical}_s{best_seed}.sol"
        )
        if best_overall_tour is not None:
            inst.save_solution_file(out_path, best_overall_tour, best_overall_cost)
            print(f"Da luu loi giai tot nhat ra tep: {out_path}")
        print("=" * 76)
        return

    # Chạy 1 lần đơn lẻ
    tour, cost, elapsed, history = run_single(inst, alg_canonical, args.seed, budget)
    is_valid, verified_cost, msg = validate_tour(inst, tour, cost)

    if len(history) > 1:
        print_convergence_evolution(history, budget)

    if alg_canonical == "NN" and tour and tour[0] == 0:
        norm_tour = list(tour)
    else:
        norm_tour = TSPInstance.normalize_tour_start_at_zero(tour)
    tour_1based = [v + 1 for v in norm_tour]
    gap_pct = ((verified_cost - inst.bks) / inst.bks * 100.0) if inst.bks else 0.0

    if args.out:
        out_path = args.out
    else:
        if alg_canonical in ("SA", "TS", "GA", "ACO", "Memetic"):
            out_path = os.path.join(
                ROOT_DIR, "results", "solutions", f"{inst.name}_{alg_canonical}_s{args.seed}.sol"
            )
        else:
            out_path = os.path.join(
                ROOT_DIR, "results", "solutions", f"{inst.name}_{alg_canonical}.sol"
            )

    inst.save_solution_file(out_path, norm_tour, verified_cost)

    print("\n  [KET QUA DAT DUOC]")
    print(f"  - Do dai chu trinh (Cost): {int(round(verified_cost))}")
    if inst.bks is not None:
        print(f"  - Do lech so voi BKS     : {gap_pct:.3f}% (BKS = {int(round(inst.bks))})")
    print(f"  - Thoi gian chay         : {elapsed:.5f} giay ({elapsed * 1000:.2f} ms)")
    print(f"  - Kiem tra hop le doc lap: {'HOP LE' if is_valid else 'KHONG HOP LE'} ({msg})")
    if inst.n <= 25:
        print(f"  - Hoan vi dinh (1..n)    : {' '.join(map(str, tour_1based))}")
    else:
        preview = " ".join(map(str, tour_1based[:12])) + " ... " + " ".join(map(str, tour_1based[-4:]))
        print(f"  - Hoan vi dinh (1..n)    : {preview}")
    print(f"  - Tep loi giai da luu    : {out_path}")

    rec = lookup_recorded_run(inst.name, alg_canonical, args.seed)
    if rec:
        print("\n  [DOI CHIEU KET QUA GHI TRONG BAO CAO (results/raw_runs.csv)]")
        print(
            f"  - Dòng lưu trong CSV (instance={rec['instance']}, algo={rec['algorithm']}, seed={rec['seed']}): "
            f"Cost = {float(rec['cost']):.0f}, Gap = {float(rec['gap_percent']):.3f}%"
        )
    print("=" * 76)


if __name__ == "__main__":
    main()
