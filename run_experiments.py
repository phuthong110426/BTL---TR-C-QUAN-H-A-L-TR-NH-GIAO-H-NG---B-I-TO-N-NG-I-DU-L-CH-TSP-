"""
Kịch bản chạy thực nghiệm tổng thể cho Đề tài 1: Bài toán Người du lịch (TSP).
Thực hiện đầy đủ các yêu cầu tại Mục 2.2, 2.3 và 3.3:
1. Sinh và lưu các bộ dữ liệu chuẩn TSPLIB & dữ liệu tự sinh.
2. Thực nghiệm Thuật toán chính xác (Held-Karp & Branch-and-Bound) trên dữ liệu nhỏ (n = 10..19)
   để tìm nghiệm tối ưu làm mốc chuẩn (ground-truth) và khảo sát giới hạn kích thước giải được.
3. Thực nghiệm các Heuristic xây dựng (Nearest Neighbor, Multi-Start NN, Cheapest Insertion)
   và Tìm kiếm cục bộ (2-opt, Swap, Or-opt với cả First Improvement và Best Improvement).
4. Thực nghiệm 5 giải thuật Metaheuristic (SA, TS, GA, ACO, Memetic):
   - Chạy 10 lần độc lập với 10 seed cố định (1001..1010) trên 12 thể hiện (3 mức kích thước).
   - Mọi lời giải đều qua hàm kiểm tra tính hợp lệ độc lập `validate_tour`.
   - Xuất tệp kết quả thô `results/raw_runs.csv` và bảng tổng hợp `results/summary_results.csv`.
5. Phân tích độ nhạy tham số (Parameter Sensitivity Analysis) cho từng metaheuristic trên `berlin52`.
6. Kiểm định thống kê phi tham số (Friedman Test & Wilcoxon Signed-Rank Test).
7. Mở rộng: Giải thể hiện lớn n = 1000 đỉnh sử dụng Candidate List.
8. Xuất các biểu đồ đường hội tụ và sơ đồ lộ trình chuẩn SVG vào `results/plots/`.
"""

import csv
import json
import math
import os
import platform
import statistics
import sys
import time
from typing import List, Dict, Any

from src.tsp_instance import TSPInstance
from src.validator import validate_tour
from src.exact_solver import solve_held_karp, solve_branch_and_bound
from src.constructive import nearest_neighbor, multi_start_nearest_neighbor, cheapest_insertion
from src.local_search import hill_climbing_2opt, hill_climbing_swap, hill_climbing_or_opt
from src.metaheuristics import (
    simulated_annealing,
    tabu_search,
    genetic_algorithm,
    ant_colony_optimization,
    memetic_algorithm,
)
from src.statistical_tests import wilcoxon_signed_rank, friedman_test
from src.datasets import build_all_datasets
from src.plotter import save_convergence_svg, save_tour_svg


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
PLOTS_DIR = os.path.join(RESULTS_DIR, "plots")

SEEDS = [1001 + i for i in range(10)]  # 10 seed độc lập tái lập 100%


def get_budget_seconds(n: int) -> float:
    """Thiết lập ngân sách thời gian công bằng (fair time budget) theo kích thước thể hiện n."""
    if n <= 20:
        return 0.12
    elif n <= 60:
        return 0.35
    elif n <= 80:
        return 0.45
    else:
        return 0.60


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)

    print("=" * 75)
    print("BẮT ĐẦU THỰC NGHIỆM ĐỀ TÀI 1: BÀI TOÁN NGƯỜI DU LỊCH (TSP)")
    print(f"Python: {sys.version.split()[0]} | OS: {platform.system()} {platform.release()}")
    print("=" * 75)

    datasets = build_all_datasets(DATA_DIR)
    small_instances = datasets["small"]
    tsplib_instances = datasets["tsplib"]
    large_syn_instances = datasets["large_syn"][:2]  # syn_40, syn_80 (hoặc syn_120)
    # Lấy syn_40, syn_80, syn_120 để có tổng cộng 5 (nhỏ) + 5 (TSPLIB) + 2 (vừa/lớn) = 12 thể hiện
    selected_large_syn = [datasets["large_syn"][0], datasets["large_syn"][2]]  # syn_40 (n=40), syn_120 (n=120)

    all_instances: List[TSPInstance] = small_instances + selected_large_syn[:1] + tsplib_instances + selected_large_syn[1:]

    # --------------------------------------------------------------------------
    # BƯỚC 1: THUẬT TOÁN CHÍNH XÁC (HELD-KARP & NHÁNH CẬN) TRÊN DỮ LIỆU NHỎ
    # --------------------------------------------------------------------------
    print("\n[1/6] Chạy thuật toán chính xác (Held-Karp & Branch-and-Bound) trên dữ liệu nhỏ...")
    exact_rows: List[Dict[str, Any]] = []

    for inst in small_instances:
        tour_hk, cost_hk, time_hk, opt_hk = solve_held_karp(inst, time_limit=60.0)
        inst.bks = cost_hk  # Đặt nghiệm tối ưu của Held-Karp làm mốc chuẩn BKS

        # Khởi tạo cận trên cho Nhánh cận bằng Nearest Neighbor
        init_t, _, _ = nearest_neighbor(inst, 0)
        tour_bb, cost_bb, time_bb, opt_bb, nodes_bb = solve_branch_and_bound(
            inst, time_limit=15.0, initial_tour=init_t
        )

        exact_rows.append({
            "instance": inst.name,
            "n": inst.n,
            "hk_cost": round(cost_hk, 2),
            "hk_time_sec": round(time_hk, 5),
            "hk_optimal": opt_hk,
            "bb_cost": round(cost_bb, 2),
            "bb_time_sec": round(time_bb, 5),
            "bb_optimal": opt_bb,
            "bb_nodes": nodes_bb,
        })
        print(
            f"  - {inst.name:8s} (n={inst.n:2d}): Opt Cost = {cost_hk:7.1f} | "
            f"Held-Karp: {time_hk:.4f}s | B&B: {time_bb:.4f}s ({nodes_bb} nút)"
        )

    # Khảo sát thêm mốc n = 19, 20, 21 cho Held-Karp để đánh giá sự bùng nổ tổ hợp O(n^2 2^n)
    for n_test in (19, 20, 21):
        inst_scale = TSPInstance.generate_random(n=n_test, seed=900 + n_test, name=f"scale_{n_test}")
        _, c_hk, t_hk, o_hk = solve_held_karp(inst_scale, time_limit=120.0)
        exact_rows.append({
            "instance": inst_scale.name,
            "n": n_test,
            "hk_cost": round(c_hk, 2),
            "hk_time_sec": round(t_hk, 5),
            "hk_optimal": o_hk,
            "bb_cost": "-",
            "bb_time_sec": "-",
            "bb_optimal": "-",
            "bb_nodes": "-",
        })
        print(f"  - {inst_scale.name:8s} (n={n_test:2d}): Opt Cost = {c_hk:7.1f} | Held-Karp: {t_hk:.4f}s")

    with open(os.path.join(RESULTS_DIR, "exact_results.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(exact_rows[0].keys()))
        writer.writeheader()
        writer.writerows(exact_rows)

    # --------------------------------------------------------------------------
    # BƯỚC 2: HEURISTIC XÂY DỰNG VÀ TÌM KIẾM CỤC BỘ (FIRST vs BEST IMPROVEMENT)
    # --------------------------------------------------------------------------
    print("\n[2/6] Chạy Heuristic xây dựng (NN, Multi-NN, CI) và Tìm kiếm cục bộ (2-opt, Swap, Or-opt)...")
    heuristic_rows: List[Dict[str, Any]] = []

    for inst in all_instances:
        t_nn, c_nn, time_nn = nearest_neighbor(inst, 0)
        t_msnn, c_msnn, time_msnn = multi_start_nearest_neighbor(inst, max_starts=min(inst.n, 30))
        t_ci, c_ci, time_ci = cheapest_insertion(inst, 0)

        # Tìm kiếm cục bộ xuất phát từ lời giải Nearest Neighbor (đỉnh 0)
        t_2opt_fi, c_2opt_fi, time_2opt_fi, steps_2opt_fi, _ = hill_climbing_2opt(inst, t_nn, strategy="first")
        t_2opt_bi, c_2opt_bi, time_2opt_bi, steps_2opt_bi, _ = hill_climbing_2opt(inst, t_nn, strategy="best")
        t_swap_fi, c_swap_fi, time_swap_fi, steps_swap_fi, _ = hill_climbing_swap(inst, t_nn, strategy="first")
        t_swap_bi, c_swap_bi, time_swap_bi, steps_swap_bi, _ = hill_climbing_swap(inst, t_nn, strategy="best")
        t_or_fi, c_or_fi, time_or_fi, steps_or_fi, _ = hill_climbing_or_opt(inst, t_nn, strategy="first")
        t_or_bi, c_or_bi, time_or_bi, steps_or_bi, _ = hill_climbing_or_opt(inst, t_nn, strategy="best")

        # Nếu thể hiện tự sinh lớn chưa có BKS, tạm lấy min của các phương pháp (sẽ cập nhật sau khi chạy Metaheuristic)
        heuristic_rows.append({
            "instance": inst.name,
            "n": inst.n,
            "bks": inst.bks if inst.bks is not None else 0.0,
            "nn_cost": round(c_nn, 2),
            "nn_time_ms": round(time_nn * 1000, 3),
            "msnn_cost": round(c_msnn, 2),
            "msnn_time_ms": round(time_msnn * 1000, 3),
            "ci_cost": round(c_ci, 2),
            "ci_time_ms": round(time_ci * 1000, 3),
            "hc_2opt_first_cost": round(c_2opt_fi, 2),
            "hc_2opt_first_time_ms": round(time_2opt_fi * 1000, 3),
            "hc_2opt_first_steps": steps_2opt_fi,
            "hc_2opt_best_cost": round(c_2opt_bi, 2),
            "hc_2opt_best_time_ms": round(time_2opt_bi * 1000, 3),
            "hc_2opt_best_steps": steps_2opt_bi,
            "hc_swap_first_cost": round(c_swap_fi, 2),
            "hc_swap_first_time_ms": round(time_swap_fi * 1000, 3),
            "hc_swap_best_cost": round(c_swap_bi, 2),
            "hc_swap_best_time_ms": round(time_swap_bi * 1000, 3),
            "hc_oropt_first_cost": round(c_or_fi, 2),
            "hc_oropt_first_time_ms": round(time_or_fi * 1000, 3),
            "hc_oropt_best_cost": round(c_or_bi, 2),
            "hc_oropt_best_time_ms": round(time_or_bi * 1000, 3),
        })
        print(
            f"  - {inst.name:8s} (n={inst.n:3d}): NN={c_nn:7.0f}, CI={c_ci:7.0f} | "
            f"2-opt(FI)={c_2opt_fi:7.0f}, 2-opt(BI)={c_2opt_bi:7.0f}, Swap(FI)={c_swap_fi:7.0f}, Or-opt(FI)={c_or_fi:7.0f}"
        )

    with open(os.path.join(RESULTS_DIR, "constructive_localsearch.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(heuristic_rows[0].keys()))
        writer.writeheader()
        writer.writerows(heuristic_rows)

    # --------------------------------------------------------------------------
    # BƯỚC 3: THỰC NGHIỆM 5 METAHEURISTIC (10 LẦN ĐỘC LẬP / THỂ HIỆN)
    # --------------------------------------------------------------------------
    print("\n[3/6] Chạy 5 giải thuật Metaheuristic (SA, TS, GA, ACO, Memetic) x 10 seeds trên 12 thể hiện...")
    raw_runs: List[Dict[str, Any]] = []
    summary_rows: List[Dict[str, Any]] = []

    alg_list = ["SA", "TS", "GA", "ACO", "Memetic"]
    # Ma trận lưu Mean Cost (12 thể hiện x 5 thuật toán) để chạy kiểm định thống kê
    perf_matrix_mean: List[List[float]] = []

    for inst in all_instances:
        budget = get_budget_seconds(inst.n)
        inst_curves: Dict[str, List[ Any ]] = {}
        inst_best_tours: Dict[str, Tuple[List[int], float]] = {}
        inst_alg_runs: Dict[str, List[Tuple[int, int, float, float, List[int]]]] = {a: [] for a in alg_list}

        for alg in alg_list:
            for run_idx, seed in enumerate(SEEDS, start=1):
                if alg == "SA":
                    tour, cost, elapsed, hist = simulated_annealing(inst, seed=seed, time_limit=budget)
                elif alg == "TS":
                    tour, cost, elapsed, hist = tabu_search(inst, seed=seed, time_limit=budget)
                elif alg == "GA":
                    tour, cost, elapsed, hist = genetic_algorithm(inst, seed=seed, time_limit=budget)
                elif alg == "ACO":
                    tour, cost, elapsed, hist = ant_colony_optimization(inst, seed=seed, time_limit=budget)
                elif alg == "Memetic":
                    tour, cost, elapsed, hist = memetic_algorithm(inst, seed=seed, time_limit=budget)
                else:
                    raise ValueError(f"Unknown algorithm {alg}")

                # Kiểm tra tính hợp lệ độc lập
                is_valid, verified_cost, msg = validate_tour(inst, tour, cost)
                if not is_valid:
                    raise RuntimeError(f"Lời giải không hợp lệ: {alg} trên {inst.name}: {msg}")

                inst_alg_runs[alg].append((run_idx, seed, verified_cost, elapsed, tour))

                if run_idx == 1:
                    inst_curves[alg] = hist
                if alg not in inst_best_tours or verified_cost < inst_best_tours[alg][1]:
                    inst_best_tours[alg] = (tour, verified_cost)

        # Nếu thể hiện tự sinh lớn (syn_40, syn_120) chưa có BKS từ chuẩn TSPLIB,
        # đặt BKS là giá trị tốt nhất tìm được trên toàn bộ các lần chạy của mọi thuật toán
        if inst.bks is None:
            inst.bks = min(
                cost_val
                for alg in alg_list
                for (_, _, cost_val, _, _) in inst_alg_runs[alg]
            )

        bks = inst.bks
        row_means_for_stat: List[float] = []

        for alg in alg_list:
            runs = inst_alg_runs[alg]
            costs = [r[2] for r in runs]
            times = [r[3] for r in runs]

            for r_id, s_val, c_val, t_val, _ in runs:
                gap_val = ((c_val - bks) / bks) * 100.0
                raw_runs.append({
                    "instance": inst.name,
                    "n": inst.n,
                    "bks": round(bks, 2),
                    "algorithm": alg,
                    "run_id": r_id,
                    "seed": s_val,
                    "cost": round(c_val, 2),
                    "gap_percent": round(gap_val, 4),
                    "time_sec": round(t_val, 4),
                    "valid": True,
                })

            best_c = min(costs)
            mean_c = statistics.mean(costs)
            std_c = statistics.stdev(costs) if len(costs) > 1 else 0.0
            mean_t = statistics.mean(times)
            best_gap = ((best_c - bks) / bks) * 100.0
            mean_gap = ((mean_c - bks) / bks) * 100.0
            opt_hits = sum(1 for c in costs if abs(c - bks) <= 1e-4)
            hit_rate = (opt_hits / len(costs)) * 100.0

            row_means_for_stat.append(mean_c)
            summary_rows.append({
                "instance": inst.name,
                "n": inst.n,
                "bks": round(bks, 2),
                "algorithm": alg,
                "best_cost": round(best_c, 2),
                "mean_cost": round(mean_c, 2),
                "std_cost": round(std_c, 2),
                "best_gap_pct": round(best_gap, 3),
                "mean_gap_pct": round(mean_gap, 3),
                "mean_time_sec": round(mean_t, 4),
                "opt_hit_rate_pct": round(hit_rate, 1),
            })

        perf_matrix_mean.append(row_means_for_stat)

        # Vẽ biểu đồ đường hội tụ và lộ trình tốt nhất cho các thể hiện đại diện
        save_convergence_svg(
            os.path.join(PLOTS_DIR, f"convergence_{inst.name}.svg"),
            instance_name=inst.name,
            curves=inst_curves,
            bks=bks,
        )
        best_overall_alg = min(alg_list, key=lambda a: inst_best_tours[a][1])
        best_t, best_c = inst_best_tours[best_overall_alg]
        save_tour_svg(
            os.path.join(PLOTS_DIR, f"tour_{inst.name}.svg"),
            instance=inst,
            tour=best_t,
            alg_name=best_overall_alg,
            cost=best_c,
        )

        # In tóm tắt nhanh trên console
        summary_str = " | ".join(
            f"{a}: best={min(r[2] for r in inst_alg_runs[a]):.0f} (mean={statistics.mean(r[2] for r in inst_alg_runs[a]):.1f})"
            for a in alg_list
        )
        print(f"  - {inst.name:8s} (n={inst.n:3d}, BKS={bks:6.0f}): {summary_str}")

    with open(os.path.join(RESULTS_DIR, "raw_runs.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(raw_runs[0].keys()))
        writer.writeheader()
        writer.writerows(raw_runs)

    with open(os.path.join(RESULTS_DIR, "summary_results.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    # --------------------------------------------------------------------------
    # BƯỚC 4: PHÂN TÍCH ĐỘ NHẠY THAM SỐ (PARAMETER SENSITIVITY) TRÊN BERLIN52
    # --------------------------------------------------------------------------
    print("\n[4/6] Phân tích độ nhạy tham số trên bộ dữ liệu chuẩn berlin52 (BKS = 7542)...")
    berlin = next(inst for inst in tsplib_instances if inst.name == "berlin52")
    sens_rows: List[Dict[str, Any]] = []
    sens_seeds = SEEDS[:5]  # 5 lần chạy cho mỗi cấu hình tham số

    # 4.1 SA: Hệ số làm nguội alpha
    for alpha_val in (0.95, 0.985, 0.995, 0.999):
        costs = [simulated_annealing(berlin, seed=s, alpha=alpha_val, time_limit=0.6)[1] for s in sens_seeds]
        sens_rows.append({
            "algorithm": "SA",
            "parameter": "alpha (cooling rate)",
            "value": str(alpha_val),
            "best_cost": round(min(costs), 2),
            "mean_cost": round(statistics.mean(costs), 2),
            "std_cost": round(statistics.stdev(costs), 2),
            "mean_gap_pct": round((statistics.mean(costs) - berlin.bks) / berlin.bks * 100.0, 3),
        })

    # 4.2 TS: Độ dài danh sách Tabu (tabu_tenure)
    for tenure_val in (5, 15, 30, 50):
        costs = [tabu_search(berlin, seed=s, tabu_tenure=tenure_val, time_limit=0.6)[1] for s in sens_seeds]
        sens_rows.append({
            "algorithm": "TS",
            "parameter": "tabu_tenure",
            "value": str(tenure_val),
            "best_cost": round(min(costs), 2),
            "mean_cost": round(statistics.mean(costs), 2),
            "std_cost": round(statistics.stdev(costs), 2),
            "mean_gap_pct": round((statistics.mean(costs) - berlin.bks) / berlin.bks * 100.0, 3),
        })

    # 4.3 GA: Toán tử lai ghép (OX vs PMX) và xác suất đột biến
    for cx_type, mut_val in (("OX", 0.05), ("OX", 0.20), ("OX", 0.35), ("PMX", 0.20)):
        costs = [
            genetic_algorithm(berlin, seed=s, crossover_type=cx_type, mutation_rate=mut_val, time_limit=0.6)[1]
            for s in sens_seeds
        ]
        sens_rows.append({
            "algorithm": "GA",
            "parameter": "crossover + mutation_rate",
            "value": f"{cx_type}, pm={mut_val}",
            "best_cost": round(min(costs), 2),
            "mean_cost": round(statistics.mean(costs), 2),
            "std_cost": round(statistics.stdev(costs), 2),
            "mean_gap_pct": round((statistics.mean(costs) - berlin.bks) / berlin.bks * 100.0, 3),
        })

    # 4.4 ACO: Trọng số heuristic beta và bay hơi rho
    for beta_val, rho_val in ((1.0, 0.15), (3.0, 0.15), (5.0, 0.15), (3.0, 0.35)):
        costs = [
            ant_colony_optimization(berlin, seed=s, beta=beta_val, rho=rho_val, time_limit=0.6)[1]
            for s in sens_seeds
        ]
        sens_rows.append({
            "algorithm": "ACO",
            "parameter": "beta, rho",
            "value": f"beta={beta_val}, rho={rho_val}",
            "best_cost": round(min(costs), 2),
            "mean_cost": round(statistics.mean(costs), 2),
            "std_cost": round(statistics.stdev(costs), 2),
            "mean_gap_pct": round((statistics.mean(costs) - berlin.bks) / berlin.bks * 100.0, 3),
        })

    with open(os.path.join(RESULTS_DIR, "parameter_sensitivity.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(sens_rows[0].keys()))
        writer.writeheader()
        writer.writerows(sens_rows)

    # --------------------------------------------------------------------------
    # BƯỚC 5: KIỂM ĐỊNH THỐNG KÊ (FRIEDMAN & WILCOXON SIGNED-RANK)
    # --------------------------------------------------------------------------
    print("\n[5/6] Thực hiện kiểm định thống kê Friedman và Wilcoxon Signed-Rank...")
    friedman_res = friedman_test(alg_list, perf_matrix_mean)
    print(f"  - Friedman Test (N={friedman_res['n_instances']}, df={friedman_res['df']}): "
          f"Chi2 = {friedman_res['chi2_stat']}, F_ID = {friedman_res['f_stat']}, p-value = {friedman_res['p_value']}")
    print(f"  - Hạng trung bình (Average Ranks): {friedman_res['avg_ranks']}")

    # Kiểm định cặp Wilcoxon giữa Memetic (cột 4) và từng thuật toán còn lại trên 12 thể hiện
    memetic_col = [row[4] for row in perf_matrix_mean]
    wilcoxon_rows: List[Dict[str, Any]] = []
    for idx, other_alg in enumerate(alg_list[:-1]):
        other_col = [row[idx] for row in perf_matrix_mean]
        w_res = wilcoxon_signed_rank(other_col, memetic_col)
        wilcoxon_rows.append({
            "comparison": f"{other_alg} vs Memetic",
            "w_plus": w_res["w_plus"],
            "w_minus": w_res["w_minus"],
            "w_stat": w_res["w_stat"],
            "z_score": w_res["z_score"],
            "p_value": w_res["p_value"],
            "method": w_res.get("method", "exact"),
            "n_effective": w_res["n_effective"],
            "significant_alpha_005": w_res["p_value"] < 0.05,
        })
        print(f"  - Wilcoxon ({other_alg:3s} vs Memetic): W+={w_res['w_plus']}, W-={w_res['w_minus']}, "
              f"Z={w_res['z_score']}, p={w_res['p_value']}")

    with open(os.path.join(RESULTS_DIR, "wilcoxon_results.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(wilcoxon_rows[0].keys()))
        writer.writeheader()
        writer.writerows(wilcoxon_rows)

    with open(os.path.join(RESULTS_DIR, "statistical_summary.json"), "w", encoding="utf-8") as f:
        json.dump(
            {"friedman": friedman_res, "wilcoxon_vs_memetic": wilcoxon_rows},
            f,
            indent=2,
            ensure_ascii=False,
        )

    # --------------------------------------------------------------------------
    # BƯỚC 6: THỬ NGHIỆM MỞ RỘNG TRÊN THỂ HIỆN CỠ LỚN N = 1000 VỚI CANDIDATE LIST
    # --------------------------------------------------------------------------
    print("\n[6/6] Thử nghiệm mở rộng (Mục 5 Đề 1): Thể hiện lớn n = 1000 dùng Candidate List (k=20)...")
    inst_1000 = TSPInstance.generate_random(n=1000, seed=2026, name="syn_1000", box_size=10000.0, clustered=True)
    t_nn_1k, c_nn_1k, time_nn_1k = nearest_neighbor(inst_1000, 0)
    t_2opt_1k, c_2opt_1k, time_2opt_1k, steps_1k, _ = hill_climbing_2opt(
        inst_1000, t_nn_1k, strategy="first", max_iters=3000, use_candidate_list=True
    )
    improv_1k = (c_nn_1k - c_2opt_1k) / c_nn_1k * 100.0
    print(
        f"  - syn_1000 (n=1000): NN Cost = {c_nn_1k:.0f} ({time_nn_1k:.3f}s) -> "
        f"Candidate-List 2-opt Cost = {c_2opt_1k:.0f} ({time_2opt_1k:.3f}s, {steps_1k} bước, cải thiện {improv_1k:.2f}%)"
    )

    with open(os.path.join(RESULTS_DIR, "large_scale_1000.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "instance": "syn_1000",
                "n": 1000,
                "candidate_k": 20,
                "nn_cost": round(c_nn_1k, 2),
                "nn_time_sec": round(time_nn_1k, 4),
                "cl_2opt_cost": round(c_2opt_1k, 2),
                "cl_2opt_time_sec": round(time_2opt_1k, 4),
                "cl_2opt_steps": steps_1k,
                "improvement_pct": round(improv_1k, 2),
            },
            f,
            indent=2,
        )

    print("\nHOÀN TẤT TOÀN BỘ THỰC NGHIỆM! Kết quả đã được lưu tại:", RESULTS_DIR)


if __name__ == "__main__":
    main()
