# BÀI TẬP LỚN HỌC PHẦN: PHÂN TÍCH THIẾT KẾ GIẢI THUẬT
## Đề tài 1: Lộ trình xe giao hàng — Bài toán Người du lịch (Traveling Salesman Problem - TSP)

- **Trường:** Đại học Giao thông Vận tải TP. Hồ Chí Minh (UTH) — Ngành Công nghệ thông tin
- **Chủ đề:** Các bài toán NP-khó và Giải thuật Metaheuristic
- **Quy mô nhóm:** 4 thành viên (Đầy đủ: Thuật toán chính xác + Heuristic xây dựng + Tìm kiếm cục bộ + 4 Metaheuristic đơn lời giải & quần thể + 1 Thuật toán Lai Memetic + Phân tích độ nhạy tham số + Kiểm định thống kê Friedman & Wilcoxon + Giao diện trực quan hóa Web/Desktop GUI).

---

## 1. Cấu trúc thư mục dự án

```text
btl_tsp_de1/
├── README.md                       # Hướng dẫn cài đặt, chạy và tái lập kết quả thực nghiệm
├── run_experiments.py              # Kịch bản chạy toàn bộ thực nghiệm, xuất CSV, kiểm định thống kê & vẽ biểu đồ SVG
├── gui_visualizer.py               # Giao diện trực quan hóa Desktop (Python Tkinter GUI)
├── visualizer/
│   └── index.html                  # Giao diện trực quan hóa Web tương tác thời gian thực (HTML5 Canvas)
├── src/
│   ├── __init__.py
│   ├── tsp_instance.py             # Đọc/ghi tệp chuẩn TSPLIB (.tsp), sinh dữ liệu có seed, Candidate List
│   ├── validator.py                # Hàm kiểm tra tính hợp lệ độc lập của lời giải (Mục 3.1.5)
│   ├── exact_solver.py             # Quy hoạch động Held–Karp O(n^2 2^n) và Nhánh cận (Branch & Bound)
│   ├── constructive.py             # Tham lam: Nearest Neighbor, Multi-Start NN, Cheapest Insertion
│   ├── local_search.py             # Tìm kiếm cục bộ: 2-opt, Swap, Or-opt (First & Best Improvement, Delta O(1))
│   ├── metaheuristics.py           # 4 Metaheuristic (SA, TS, GA, ACO) + 1 Thuật toán Lai (Memetic Algorithm)
│   ├── statistical_tests.py        # Kiểm định phi tham số: Friedman Test & Wilcoxon Signed-Rank Test
│   ├── datasets.py                 # Quản lý bộ dữ liệu chuẩn TSPLIB & bộ dữ liệu tự sinh
│   └── plotter.py                  # Xuất biểu đồ hội tụ và sơ đồ chu trình chuẩn Vector (SVG)
├── data/
│   ├── tsplib/                     # Các bộ dữ liệu chuẩn TSPLIB (eil51, berlin52, st70, eil76, kroA100)
│   └── synthetic/                  # Các bộ dữ liệu tự sinh (syn_10..syn_18, syn_40, syn_80, syn_120, syn_150)
├── results/
│   ├── exact_results.csv           # Kết quả đối chiếu Held–Karp và Nhánh cận trên dữ liệu nhỏ
│   ├── constructive_localsearch.csv# Kết quả Heuristic xây dựng & Tìm kiếm cục bộ (First vs Best Improvement)
│   ├── raw_runs.csv                # Kết quả thô của toàn bộ 600 lần chạy (12 thể hiện x 5 thuật toán x 10 seeds)
│   ├── summary_results.csv         # Bảng tổng hợp: Best, Mean, Std, Gap (%), Thời gian TB, Tỉ lệ đạt tối ưu
│   ├── parameter_sensitivity.csv   # Kết quả phân tích độ nhạy tham số trên berlin52
│   ├── wilcoxon_results.csv        # Kết quả kiểm định dấu hạng Wilcoxon
│   ├── statistical_summary.json    # Kết quả kiểm định Friedman (Chi2, Iman-Davenport F, Average Ranks)
│   ├── large_scale_1000.json       # Kết quả mở rộng trên thể hiện lớn n = 1000 dùng Candidate List
│   └── plots/                      # Các biểu đồ đường hội tụ (convergence_*.svg) và lộ trình (tour_*.svg)
└── report/
    ├── BAO_CAO_BTL_TSP_DE1.md      # Nội dung Báo cáo chi tiết đầy đủ theo khung Mục 2.3
    ├── BAO_CAO_BTL_TSP_DE1.tex     # Mã nguồn LaTeX chuẩn học thuật để biên dịch ra PDF
    └── SLIDE_THUYET_TRINH_TSP_DE1.md # Nội dung Slide thuyết trình (15-20 phút) + Kịch bản Demo
```

---

## 2. Yêu cầu hệ thống & Cài đặt

Dự án được thiết kế bằng **Python 3.10+** sử dụng hoàn toàn thư viện chuẩn của Python (`math`, `random`, `array`, `csv`, `json`, `time`, `statistics`, `tkinter`) để bảo đảm **chạy được ngay lập tức trên mọi máy tính mà không gặp lỗi thiếu thư viện ngoài**.

- **Phiên bản Python đã kiểm thử:** Python 3.14.7 (`D:\msys64\ucrt64\bin\python.exe` hoặc `python` trong PATH).
- **Hệ điều hành:** Windows 10 / 11, Linux, hoặc macOS.

---

## 3. Hướng dẫn chạy và tái lập kết quả thực nghiệm (Reproducibility)

### 3.1. Chạy toàn bộ thực nghiệm và xuất tệp CSV + Biểu đồ SVG
Mở Terminal / PowerShell tại thư mục dự án và chạy:

```powershell
python run_experiments.py
```
*(Nếu dùng Python trong MSYS64 trên máy hiện tại)*:
```powershell
D:\msys64\ucrt64\bin\python.exe run_experiments.py
```

**Thông số tái lập kết quả (Seeds & Tham số mặc định):**
- Tập 10 hạt giống ngẫu nhiên độc lập (Seeds): `SEEDS = [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010]`.
- Dữ liệu nhỏ tự sinh cố định seed: `syn_10` (`seed=101`), `syn_12` (`seed=102`), `syn_15` (`seed=105`), `syn_16` (`seed=106`), `syn_18` (`seed=108`).
- Dữ liệu vừa/lớn tự sinh cố định seed: `syn_40` (`seed=204`), `syn_80` (`seed=208`), `syn_120` (`seed=212`), `syn_1000` (`seed=2026`).
- Tham số mặc định của các Metaheuristic:
  - **SA (Simulated Annealing):** $T_0 = \frac{f(\text{NN})}{2n}$, hệ số làm nguội $\alpha = 0.995$, $L = \min(200, 2n)$ bước/mức nhiệt, $T_{\min} = 10^{-3}$.
  - **TS (Tabu Search):** Độ dài cấm $\text{tenure} = \lfloor 2.5\sqrt{n} \rfloor \pm 2$, kích thước mẫu lân cận 2-opt $= \max(60, 3n)$, có tiêu chí mong đợi (Aspiration Criterion).
  - **GA (Genetic Algorithm):** Kích thước quần thể $\text{pop\_size} = 60$, xác suất lai $p_c = 0.85$ (Order Crossover - OX), xác suất đột biến $p_m = 0.20$ (Inversion + Swap), ưu tú $\text{elite\_size} = 4$.
  - **ACO (Ant Colony Optimization - MMAS/ACS):** Số kiến $m = 25$, $\alpha = 1.0$, $\beta = 3.0$, hệ số bay hơi $\rho = 0.15$, ngưỡng khai thác $q_0 = 0.5$, kết hợp Candidate List ($k = 20$).
  - **Memetic Algorithm (Thuật toán Lai GA + 2-opt + Double-Bridge):** $\text{pop\_size} = 30$, $p_c = 0.90$ (OX), $p_m = 0.25$ (nhiễu 4-opt Double-Bridge), kết hợp tìm kiếm cục bộ 2-opt First Improvement trên mỗi cá thể con.

### 3.2. Chạy Giao diện Trực quan hóa (Visualizer) để Demo & Thuyết trình
Nhóm cung cấp 2 giao diện trực quan hóa:

1. **Giao diện Web tương tác thời gian thực (Khuyên dùng khi thuyết trình):**
   Mở trực tiếp tệp `visualizer/index.html` trên trình duyệt (Chrome / Edge / Opera / Firefox).
   - Hỗ trợ chọn trực tiếp các bộ dữ liệu chuẩn TSPLIB (`eil51`, `berlin52`, `st70`, `eil76`, `kroA100`) hoặc sinh ngẫu nhiên tới $N = 1000$ đỉnh.
   - Xem trực tiếp quá trình biến đổi chu trình từng bước và đồ thị đường hội tụ theo thời gian thực.

2. **Giao diện Python Tkinter Desktop GUI:**
   ```powershell
   D:\msys64\ucrt64\bin\python.exe gui_visualizer.py
   ```

---

## 4. Phân công công việc nhóm (4 thành viên)

| Thành viên | Thuật toán chịu trách nhiệm chính | Phần việc chung & Thực nghiệm |
| :--- | :--- | :--- |
| **Thành viên 1** | **Simulated Annealing (SA)** + Thuật toán chính xác **Held–Karp DP** | Mô hình hóa toán học, chứng minh NP-khó, thực nghiệm dữ liệu nhỏ |
| **Thành viên 2** | **Tabu Search (TS)** + Thuật toán chính xác **Nhánh cận (B&B)** | Cài đặt Heuristic xây dựng (NN, Cheapest Insertion), hàm kiểm tra hợp lệ |
| **Thành viên 3** | **Genetic Algorithm (GA - OX/PMX)** + Tìm kiếm cục bộ (**2-opt, Swap**) | Thiết kế lân cận, đánh giá gia tăng (Delta Evaluation), phân tích độ nhạy tham số |
| **Thành viên 4** | **Ant Colony Optimization (ACO)** + **Thuật toán Lai (Memetic)** + **Or-opt** | Kiểm định thống kê (Friedman, Wilcoxon), trực quan hóa lộ trình & tổng hợp Báo cáo |
