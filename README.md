# BÀI TẬP LỚN HỌC PHẦN: PHÂN TÍCH THIẾT KẾ GIẢI THUẬT
## Đề tài 1: Lộ trình xe giao hàng — Bài toán Người du lịch (Traveling Salesman Problem - TSP)

---

## 1. Thông tin nhóm, Đề tài & Phân công tóm tắt (Mục 6.3.1)

- **Trường:** Đại học Giao thông Vận tải TP. Hồ Chí Minh (UTH) — Ngành Công nghệ thông tin
- **Học phần:** Phân tích thiết kế giải thuật (Năm học 2026–2027)
- **Chủ đề:** Các bài toán NP-khó và Giải thuật Metaheuristic
- **Đề tài:** **Đề 1 — Lộ trình xe giao hàng: Bài toán Người du lịch (TSP)** (Mức độ: Cơ bản; Quy mô: **4 thành viên**).

| Thành viên | Thuật toán chịu trách nhiệm chính | Phần việc chung, Lý thuyết & Thực nghiệm | Tỉ lệ |
| :--- | :--- | :--- | :---: |
| **Thành viên 1** | **Simulated Annealing (SA)** + Quy hoạch động **Held–Karp DP** | Mô hình hóa toán học ILP (ràng buộc DFJ/MTZ), chứng minh NP-khó, hàm kiểm tra độc lập `validator.py` | 25% |
| **Thành viên 2** | **Tabu Search (TS)** + **Nhánh cận (Branch & Bound)** | Heuristic xây dựng (Nearest Neighbor, Cheapest Insertion), Tìm kiếm cục bộ (`2-opt`, `Swap`, `Or-opt`), Delta Evaluation $\mathcal{O}(1)$ | 25% |
| **Thành viên 3** | **Genetic Algorithm (GA - OX/PMX)** | Thiết kế toán tử lai ghép hoán vị OX/PMX, quản lý bộ dữ liệu TSPLIB & tự sinh, phân tích độ nhạy tham số | 25% |
| **Thành viên 4** | **Ant Colony Optimization (ACO - MMAS)** + **Thuật toán Lai (Memetic)** | Kiểm định thống kê phi tham số (Friedman, Exact Wilcoxon), mở rộng $n=1000$ (Candidate List + Don't-Look Bits), Giao diện Web/GUI | 25% |

---

## 2. Môi trường thực thi & Cấu trúc thư mục nộp bài (Mục 6.2 & 6.3.2)

### 2.1. Môi trường phần cứng & phần mềm
- **Hệ điều hành:** Windows 10 / 11 (64-bit), tương thích hoàn toàn với Linux và macOS.
- **Ngôn ngữ lập trình:** Python 3.10+ (Đã kiểm thử thực nghiệm trên **Python 3.14.7** — `D:\msys64\ucrt64\bin\python.exe`).
- **Thư viện sử dụng:** Chỉ sử dụng **thư viện chuẩn của Python** (`math`, `random`, `array`, `csv`, `json`, `time`, `statistics`, `itertools`, `argparse`, `tkinter`). **Không phụ thuộc bất kỳ thư viện ngoài nào**, bảo đảm chạy lại được ngay trên mọi máy tính chấm bài.

### 2.2. Cấu trúc thư mục chuẩn theo Mục 6.2
```text
btl_tsp_de1/
├── README.md                       # Hướng dẫn cài đặt, chạy CLI, kiểm tra và tái lập kết quả (Mục 6.3)
├── kiemtra.py / kiemtra.bat        # Chương trình kiểm tra độc lập: kiemtra <tệp_vào> <tệp_lời_giải> (Mục 5.2 & 6.3.4)
├── solve.py / main.py              # CLI chạy 1 thuật toán trên 1 thể hiện với mọi tham số (Mục 6.3.3 & 7.2)
├── demo_baove.py / demo_baove.bat  # Script chạy tự động trọn bộ 4 bước Demo bảo vệ (Mục 7.2)
├── run_experiments.py              # Script chạy toàn bộ 600 lần thực nghiệm, kiểm định thống kê & vẽ biểu đồ
├── export_standard_results.py      # Script xuất chuẩn hóa thư mục results/{raw, conv, solutions, figures}
├── gui_visualizer.py               # Giao diện trực quan hóa Desktop (Python Tkinter GUI)
├── visualizer/
│   └── index.html                  # Giao diện trực quan hóa Web tương tác thời gian thực (HTML5 Canvas)
├── src/
│   ├── tsp_instance.py             # Đọc/ghi tệp tự định nghĩa & TSPLIB (.tsp, .opt.tour, .sol), Candidate List
│   ├── validator.py                # Hàm kiểm tra tính hợp lệ độc lập của lời giải (dòng 11–82)
│   ├── exact_solver.py             # Quy hoạch động Held–Karp O(n^2 2^n) & Nhánh cận (dòng 18–221)
│   ├── constructive.py             # Tham lam: Nearest Neighbor, Multi-Start NN, Cheapest Insertion
│   ├── local_search.py             # Tìm kiếm cục bộ: 2-opt, Swap, Or-opt, Delta O(1) (dòng 21–33), Don't-Look Bits
│   ├── metaheuristics.py           # 4 Metaheuristic (SA, TS, GA, ACO) + 1 Thuật toán Lai (Memetic Algorithm)
│   ├── statistical_tests.py        # Kiểm định phi tham số: Friedman Test & Exact Wilcoxon Signed-Rank Test
│   ├── datasets.py                 # Quản lý bộ dữ liệu chuẩn TSPLIB & bộ dữ liệu tự sinh
│   └── plotter.py                  # Xuất biểu đồ hội tụ (Trung vị + IQR 25%–75%), Boxplot & lộ trình (SVG)
├── data/
│   ├── vidu/                       # Ví dụ nhỏ 7 đỉnh trong đề (vidu.txt), lời giải tối ưu 31 (vidu.sol) & de01.py
│   ├── chuan/                      # Bộ dữ liệu chuẩn TSPLIB (eil51, berlin52, st70, eil76, kroA100, berlin52.opt.tour, LINKS.txt)
│   └── tusinh/                     # Dữ liệu tự sinh (syn_10..syn_150) + chương trình sinh có seed (sinh_du_lieu.py)
├── results/
│   ├── raw/                        # CSV kết quả thô từng thuật toán (SA.csv, TS.csv, GA.csv, ACO.csv, MEMETIC.csv...)
│   ├── conv/                       # Log hội tụ (<thể_hiện>_<thuật_toán>_s<seed>_conv.csv: time_s,iter,evals,best)
│   ├── solutions/                  # Tệp lời giải chuẩn .sol (<thể_hiện>_<thuật_toán>_s<seed>.sol)
│   └── figures/                    # Biểu đồ hội tụ IQR (convergence_iqr_*.svg), Boxplot (boxplot_*.svg), Lộ trình (tour_*.svg)
└── report/
    ├── BAO_CAO_BTL_TSP_DE1.md      # Nội dung Báo cáo chi tiết đầy đủ theo khung Mục 6.4
    ├── BAO_CAO_BTL_TSP_DE1.tex     # Mã nguồn LaTeX chuẩn học thuật (25–35 trang)
    └── SLIDE_THUYET_TRINH_TSP_DE1.html # Slide thuyết trình (15 phút) + Kịch bản thuyết trình & Vấn đáp
```

---

## 3. Lệnh chạy một thuật toán trên một thể hiện (Mục 6.3.3 & Mục 7.2)

Dự án viết bằng Python thuần nên không cần bước biên dịch. Sử dụng trực tiếp `solve.py` (hoặc `main.py`) với đầy đủ tham số dòng lệnh:

```powershell
python solve.py --instance <tệp_vào_hoặc_tên> --algo <mã_thuật_toán> --seed <seed> --budget <giây> --out <tệp_ra.sol>
```
*(Lưu ý trên máy hiện tại nếu dùng MSYS64 Python: thay `python` bằng `D:\msys64\ucrt64\bin\python.exe`)*.

- **Danh sách mã thuật toán (`--algo`):** `EXACT` (Held–Karp DP), `EXACT_BB` (Nhánh cận), `GREEDY` / `NN` (Láng giềng gần nhất), `CI` (Chèn rẻ nhất), `HC_FI` (Leo đồi 2-opt First Improvement), `HC_BI` (Leo đồi 2-opt Best Improvement), `SA`, `TS`, `GA`, `ACO`, `MEMETIC`.
- **Ví dụ chạy ngay (tương ứng 4 bước Demo bảo vệ ở Mục 7.2):**
  1. **Giải chính xác ví dụ nhỏ 7 đỉnh `vidu.txt` (ra đúng giá trị tối ưu = `31`, chu trình `1 2 3 4 5 7 6`):**
     ```powershell
     D:\msys64\ucrt64\bin\python.exe solve.py --instance data/vidu/vidu.txt --algo EXACT --out results/solutions/vidu_EXACT.sol
     ```
  2. **Chạy 1 Metaheuristic trên thể hiện chuẩn `berlin52` với `seed=1001`, hiển thị diễn biến giá trị tốt nhất:**
     ```powershell
     D:\msys64\ucrt64\bin\python.exe solve.py --instance data/chuan/berlin52.tsp --algo MEMETIC --seed 1001 --budget 0.35 --out results/solutions/berlin52_MEMETIC_s1001.sol
     ```
  3. **Tái lập 1 dòng bất kỳ trong bảng kết quả báo cáo (chạy 1 seed hoặc toàn bộ 10 seeds `1001..1010`):**
     ```powershell
     D:\msys64\ucrt64\bin\python.exe solve.py --instance kroA100 --algo MEMETIC --seed 1001
     D:\msys64\ucrt64\bin\python.exe solve.py --instance berlin52 --algo MEMETIC --all-seeds
     ```
  4. **Chạy tự động trọn bộ 4 bước Demo bảo vệ bằng 1 lệnh duy nhất:**
     ```powershell
     .\demo_baove.bat
     ```

---

## 4. Lệnh chạy chương trình kiểm tra độc lập (Mục 5.2 & 6.3.4)

Chương trình kiểm tra độc lập `kiemtra` đọc tệp dữ liệu vào và tệp lời giải, kiểm tra mọi ràng buộc hoán vị, tính lại tổng quãng đường theo chuẩn `EUC_2D` và báo `HOP LE` / `KHONG HOP LE`:

```powershell
.\kiemtra.bat <tệp_vào> <tệp_lời_giải>
# Hoặc gọi trực tiếp qua Python:
D:\msys64\ucrt64\bin\python.exe kiemtra.py <tệp_vào> <tệp_lời_giải>
```

**Ví dụ kiểm tra thực tế:**
```powershell
# 1. Kiểm tra lời giải tối ưu của ví dụ nhỏ 7 đỉnh (báo HOP LE, chi phí = 31):
.\kiemtra.bat data/vidu/vidu.txt data/vidu/vidu.sol

# 2. Kiểm tra chu trình tối ưu chuẩn TSPLIB berlin52.opt.tour (báo HOP LE, chi phí = 7542):
.\kiemtra.bat data/chuan/berlin52.tsp data/chuan/berlin52.opt.tour

# 3. Kiểm tra một tệp lời giải bất kỳ của thuật toán Memetic:
.\kiemtra.bat data/chuan/kroA100.tsp results/solutions/kroA100_MEMETIC_s1001.sol
```

---

## 5. Lệnh chạy toàn bộ thực nghiệm & Tái lập bảng/biểu đồ (Mục 6.3.5)

Để chạy lại toàn bộ thực nghiệm (Thuật toán chính xác $\rightarrow$ Heuristic & Local Search $\rightarrow$ 600 lần chạy Metaheuristic $\rightarrow$ Phân tích độ nhạy tham số $\rightarrow$ Kiểm định Friedman & Wilcoxon $\rightarrow$ Mở rộng $n=1000$ $\rightarrow$ Xuất CSV & Biểu đồ SVG):

```powershell
D:\msys64\ucrt64\bin\python.exe run_experiments.py
D:\msys64\ucrt64\bin\python.exe export_standard_results.py
```

- **Danh sách 10 hạt giống ngẫu nhiên (Seeds) cố định cho 600 lần chạy chính:**
  `SEEDS = [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010]`.
- **Danh sách hạt giống sinh dữ liệu tự sinh cố định (`data/tusinh/sinh_du_lieu.py`):**
  - Nhóm nhỏ: `syn_10` (`seed=101`), `syn_12` (`seed=102`), `syn_15` (`seed=105`), `syn_16` (`seed=106`), `syn_18` (`seed=108`).
  - Nhóm vừa & lớn: `syn_40` (`seed=204`), `syn_80` (`seed=208`), `syn_120` (`seed=212`), `syn_150` (`seed=215`), `syn_1000` (`seed=2026`).
- **Ngân sách thời gian thực tế theo quy mô đỉnh $n$:**
  - $n \le 20$: `0.12` giây/lần chạy
  - $20 < n \le 60$: `0.35` giây/lần chạy
  - $60 < n \le 80$: `0.45` giây/lần chạy
  - $n \ge 100$: `0.60` giây/lần chạy
- **Thời gian chạy ước tính toàn bộ thực nghiệm:** Khoảng **3.5 – 4.5 phút** trên máy tính cá nhân thông thường.

---

## 6. Tham số mặc định của từng Metaheuristic (Mục 6.3.6 — Trùng khớp 100% với Báo cáo)

| Giải thuật | Viết tắt | Tham số mặc định trong mã nguồn (`src/metaheuristics.py`) và Báo cáo |
| :--- | :---: | :--- |
| **Tôi luyện mô phỏng (Simulated Annealing)** | `SA` | Nhiệt độ đầu $T_0 = \frac{f(\text{NN})}{2n}$, hệ số làm nguội $\alpha = 0.995$, độ dài chuỗi Markov $L = \min(200, 2n)$ bước/mức nhiệt, ngưỡng dừng $T_{\min} = 10^{-3}$, có cơ chế hâm nóng lại (*reheating* về $0.25 T_0$). |
| **Tìm kiếm Tabu (Tabu Search)** | `TS` | Độ dài danh sách cấm động $\text{tenure} = \lfloor 2.5\sqrt{n} \rfloor + \text{rand}(-2, 2)$, kích thước mẫu lân cận 2-opt mỗi vòng $= \max(60, 3n)$, áp dụng tiêu chí mong đợi (*Aspiration Criterion*). |
| **Giải thuật Di truyền (Genetic Algorithm)** | `GA` | Kích thước quần thể $\text{pop\_size} = 60$, chọn lọc giải đấu bậc $k = 3$, xác suất lai ghép thứ tự $p_c = 0.85$ (`OX` / `PMX`), xác suất đột biến $p_m = 0.20$ (`Inversion` + `Swap`), giữ lại ưu tú $\text{elite\_size} = 4$. |
| **Tối ưu Đàn kiến (Ant Colony Optimization - MMAS)** | `ACO` | Số kiến $m = 25$, trọng số mùi $\alpha = 1.0$, trọng số heuristic khoảng cách $\beta = 3.0$, hệ số bay hơi $\rho = 0.15$, ngưỡng khai thác $q_0 = 0.5$, giới hạn $[\tau_{\min}, \tau_{\max}]$ theo MMAS, danh sách ứng viên $k = 20$. |
| **Thuật toán Lai (Memetic Algorithm)** | `MEMETIC` | Quần thể $\text{pop\_size} = 30$, xác suất lai ghép $p_c = 0.90$ (`OX`), xác suất đột biến $p_m = 0.25$, tinh chỉnh cục bộ mọi cá thể con bằng `2-opt First Improvement`, kết hợp cú đá nhiễu `4-opt Double-Bridge` khi quần thể trì trệ. |

---

## 7. Hướng dẫn mở Giao diện Trực quan hóa (Web & Desktop GUI)

1. **Giao diện Web Visualizer (Khuyên dùng khi thuyết trình):** Mở trực tiếp tệp `visualizer/index.html` trên trình duyệt.
2. **Giao diện Desktop Tkinter GUI:** Chạy lệnh `D:\msys64\ucrt64\bin\python.exe gui_visualizer.py`.
