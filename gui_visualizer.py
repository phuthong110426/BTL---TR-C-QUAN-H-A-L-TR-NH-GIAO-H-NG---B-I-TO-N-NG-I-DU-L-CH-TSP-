"""
Giao diện Trực quan hóa Desktop (Python Tkinter GUI) cho Đề tài 1: Bài toán Người du lịch (TSP).
Phục vụ thuyết trình, demo chương trình và lấy điểm cộng (+1 điểm) theo Mục 6.
Chạy lệnh:
    python gui_visualizer.py
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional

from src.tsp_instance import TSPInstance
from src.datasets import build_all_datasets
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


class TSPVisualizerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Trực quan hóa Lộ trình Xe giao hàng - Bài toán Người du lịch (TSP) - Đề tài 1")
        self.root.geometry("1180x720")
        self.root.configure(bg="#0f172a")

        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_groups = build_all_datasets(os.path.join(base_dir, "data"))
        self.instances: Dict[str, TSPInstance] = {}
        for grp in ("small", "tsplib", "large_syn"):
            for inst in data_groups[grp]:
                self.instances[inst.name] = inst

        self.current_instance: TSPInstance = self.instances["berlin52"]
        self.current_tour: List[int] = list(range(self.current_instance.n))
        self.current_cost: float = self.current_instance.tour_cost(self.current_tour)

        self._build_ui()
        self._draw_tour()

    def _build_ui(self) -> None:
        ctrl_frame = tk.Frame(self.root, bg="#1e293b", width=320, padx=14, pady=14)
        ctrl_frame.pack(side=tk.LEFT, fill=tk.Y)
        ctrl_frame.pack_propagate(False)

        tk.Label(
            ctrl_frame,
            text="ĐỀ TÀI 1: BÀI TOÁN TSP",
            font=("Segoe UI", 13, "bold"),
            fg="#38bdf8",
            bg="#1e293b",
        ).pack(anchor="w", pady=(0, 10))

        # Chọn bộ dữ liệu
        tk.Label(ctrl_frame, text="1. Chọn thể hiện (Instance):", fg="#cbd5e1", bg="#1e293b", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.inst_var = tk.StringVar(value="berlin52")
        inst_combo = ttk.Combobox(ctrl_frame, textvariable=self.inst_var, values=list(self.instances.keys()), state="readonly")
        inst_combo.pack(fill=tk.X, pady=(4, 12))
        inst_combo.bind("<<ComboboxSelected>>", self._on_instance_changed)

        # Chọn giải thuật
        tk.Label(ctrl_frame, text="2. Chọn giải thuật:", fg="#cbd5e1", bg="#1e293b", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.alg_var = tk.StringVar(value="Memetic (GA + 2-opt)")
        alg_options = [
            "Chính xác: Held-Karp DP (n <= 18)",
            "Chính xác: Nhánh cận B&B (n <= 18)",
            "Xây dựng: Nearest Neighbor (NN)",
            "Xây dựng: Cheapest Insertion (CI)",
            "Cục bộ: 2-opt (First Improvement)",
            "Cục bộ: 2-opt (Best Improvement)",
            "Cục bộ: Swap (First Improvement)",
            "Cục bộ: Or-opt (First Improvement)",
            "Metaheuristic: Simulated Annealing (SA)",
            "Metaheuristic: Tabu Search (TS)",
            "Metaheuristic: Genetic Algorithm (GA)",
            "Metaheuristic: Ant Colony (ACO)",
            "Memetic (GA + 2-opt)",
        ]
        alg_combo = ttk.Combobox(ctrl_frame, textvariable=self.alg_var, values=alg_options, state="readonly")
        alg_combo.pack(fill=tk.X, pady=(4, 12))

        # Seed và Time Limit
        param_frame = tk.Frame(ctrl_frame, bg="#1e293b")
        param_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Label(param_frame, text="Random Seed:", fg="#94a3b8", bg="#1e293b").grid(row=0, column=0, sticky="w")
        self.seed_entry = tk.Entry(param_frame, width=10)
        self.seed_entry.insert(0, "1001")
        self.seed_entry.grid(row=0, column=1, padx=6, pady=3)

        tk.Label(param_frame, text="Thời gian (giây):", fg="#94a3b8", bg="#1e293b").grid(row=1, column=0, sticky="w")
        self.time_entry = tk.Entry(param_frame, width=10)
        self.time_entry.insert(0, "1.0")
        self.time_entry.grid(row=1, column=1, padx=6, pady=3)

        run_btn = tk.Button(
            ctrl_frame,
            text="▶ CHẠY GIẢI THUẬT",
            bg="#2563eb",
            fg="#ffffff",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            pady=8,
            command=self._run_selected_algorithm,
        )
        run_btn.pack(fill=tk.X, pady=(4, 12))

        # Thông tin kết quả
        self.info_label = tk.Label(
            ctrl_frame,
            text="",
            justify=tk.LEFT,
            fg="#f8fafc",
            bg="#0f172a",
            font=("Consolas", 10),
            padx=10,
            pady=10,
        )
        self.info_label.pack(fill=tk.X, pady=(4, 10))

        # Khung vẽ Canvas bên phải
        self.canvas = tk.Canvas(self.root, bg="#0b1120", highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=12, pady=12)
        self.canvas.bind("<Configure>", lambda _e: self._draw_tour())

        self._update_info("Khởi tạo", 0.0)

    def _on_instance_changed(self, _event: object = None) -> None:
        name = self.inst_var.get()
        self.current_instance = self.instances[name]
        self.current_tour, self.current_cost, t_el = nearest_neighbor(self.current_instance, 0)
        self._update_info("Nearest Neighbor (Init)", t_el)
        self._draw_tour()

    def _update_info(self, alg_name: str, elapsed: float) -> None:
        inst = self.current_instance
        is_ok, actual_c, _ = validate_tour(inst, self.current_tour, self.current_cost)
        bks_str = f"{inst.bks:.0f}" if inst.bks else "N/A"
        gap_str = f"{(actual_c - inst.bks)/inst.bks*100:.2f}%" if inst.bks else "N/A"
        txt = (
            f"Thể hiện  : {inst.name} (n={inst.n})\n"
            f"Giải thuật: {alg_name[:22]}\n"
            f"Chi phí f : {actual_c:.1f}\n"
            f"BKS / Opt : {bks_str}\n"
            f"Độ lệch   : {gap_str}\n"
            f"Thời gian : {elapsed:.4f} s\n"
            f"Kiểm tra  : {'HỢP LỆ (OK)' if is_ok else 'LỖI'}"
        )
        self.info_label.config(text=txt)

    def _run_selected_algorithm(self) -> None:
        inst = self.current_instance
        alg = self.alg_var.get()
        seed = int(self.seed_entry.get() or 1001)
        t_limit = float(self.time_entry.get() or 1.0)

        if "Held-Karp" in alg:
            if inst.n > 19:
                messagebox.showwarning("Giới hạn kích thước", "Held-Karp chỉ chạy trực tiếp cho n <= 19!")
                return
            tour, cost, el, _ = solve_held_karp(inst, time_limit=30.0)
        elif "Nhánh cận" in alg:
            if inst.n > 19:
                messagebox.showwarning("Giới hạn kích thước", "Nhánh cận chỉ chạy trực tiếp cho n <= 19!")
                return
            tour, cost, el, _, _ = solve_branch_and_bound(inst, time_limit=15.0)
        elif "Nearest Neighbor" in alg:
            tour, cost, el = nearest_neighbor(inst, 0)
        elif "Cheapest Insertion" in alg:
            tour, cost, el = cheapest_insertion(inst, 0)
        elif "2-opt (First" in alg:
            t0, _, _ = nearest_neighbor(inst, 0)
            tour, cost, el, _, _ = hill_climbing_2opt(inst, t0, strategy="first")
        elif "2-opt (Best" in alg:
            t0, _, _ = nearest_neighbor(inst, 0)
            tour, cost, el, _, _ = hill_climbing_2opt(inst, t0, strategy="best")
        elif "Swap" in alg:
            t0, _, _ = nearest_neighbor(inst, 0)
            tour, cost, el, _, _ = hill_climbing_swap(inst, t0, strategy="first")
        elif "Or-opt" in alg:
            t0, _, _ = nearest_neighbor(inst, 0)
            tour, cost, el, _, _ = hill_climbing_or_opt(inst, t0, strategy="first")
        elif "Simulated Annealing" in alg:
            tour, cost, el, _ = simulated_annealing(inst, seed=seed, time_limit=t_limit)
        elif "Tabu Search" in alg:
            tour, cost, el, _ = tabu_search(inst, seed=seed, time_limit=t_limit)
        elif "Genetic Algorithm" in alg:
            tour, cost, el, _ = genetic_algorithm(inst, seed=seed, time_limit=t_limit)
        elif "Ant Colony" in alg:
            tour, cost, el, _ = ant_colony_optimization(inst, seed=seed, time_limit=t_limit)
        else:
            tour, cost, el, _ = memetic_algorithm(inst, seed=seed, time_limit=t_limit)

        self.current_tour = tour
        self.current_cost = cost
        self._update_info(alg, el)
        self._draw_tour()

    def _draw_tour(self) -> None:
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50 or h < 50:
            return
        pad = 45
        coords = self.current_instance.coords
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(1e-6, max_x - min_x)
        span_y = max(1e-6, max_y - min_y)

        def px(x: float) -> float:
            return pad + ((x - min_x) / span_x) * (w - 2 * pad)

        def py(y: float) -> float:
            return h - pad - ((y - min_y) / span_y) * (h - 2 * pad)

        n = len(self.current_tour)
        for i in range(n):
            u = self.current_tour[i]
            v = self.current_tour[(i + 1) % n]
            self.canvas.create_line(
                px(coords[u][0]), py(coords[u][1]),
                px(coords[v][0]), py(coords[v][1]),
                fill="#38bdf8", width=2
            )

        for idx, u in enumerate(self.current_tour):
            cx, cy = px(coords[u][0]), py(coords[u][1])
            r = 6 if idx == 0 else 4
            color = "#ef4444" if idx == 0 else "#f8fafc"
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color, outline="")


if __name__ == "__main__":
    root = tk.Tk()
    app = TSPVisualizerApp(root)
    root.mainloop()
