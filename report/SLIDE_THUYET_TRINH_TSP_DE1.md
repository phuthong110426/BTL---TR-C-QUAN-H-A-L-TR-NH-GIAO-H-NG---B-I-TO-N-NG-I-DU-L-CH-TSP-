---
marp: true
theme: default
paginate: true
---

# BÀI TẬP LỚN: PHÂN TÍCH THIẾT KẾ GIẢI THUẬT
## Đề tài 1: Lộ trình xe giao hàng — Bài toán Người du lịch (TSP)
### Chủ đề: Các bài toán NP-khó và Giải thuật Metaheuristic

- **Trường:** Đại học Giao thông Vận tải TP. Hồ Chí Minh (UTH)
- **Ngành:** Công nghệ thông tin
- **Quy mô nhóm:** 4 thành viên
- **Thời lượng trình bày:** 15–20 phút + Demo trực tiếp

---

## Slide 1: Cấu trúc bài thuyết trình (15–20 phút)

1. **Phát biểu bài toán, Mô hình toán học ILP & Tính NP-khó** *(3 phút - Thành viên 1)*
2. **Thuật toán chính xác (Held–Karp DP & Nhánh cận)** *(2 phút - Thành viên 1 & 2)*
3. **Heuristic xây dựng & Tìm kiếm cục bộ với Delta Evaluation $\mathcal{O}(1)$** *(3 phút - Thành viên 2 & 3)*
4. **Thiết kế 4 Metaheuristic (SA, TS, GA, ACO) & Thuật toán Lai Memetic** *(5 phút - Cả 4 thành viên)*
5. **Kết quả thực nghiệm 600 lần chạy, Độ nhạy tham số & Kiểm định thống kê** *(3 phút - Thành viên 3 & 4)*
6. **Demo trực tiếp chương trình & Giao diện trực quan hóa** *(3 phút - Thành viên 4)*

---

## Slide 2: Phát biểu bài toán & Ứng dụng thực tế

- **Bài toán thực tế:** Xe giao hàng xuất phát từ kho trung tâm, ghé thăm đúng một lần qua $n-1$ điểm khách hàng đã biết tọa độ và quay về kho với tổng quãng đường nhỏ nhất.
- **Ứng dụng rộng rãi:**
  - Giao hàng chặng cuối (*Last-mile delivery*), thu gom rác thải đô thị.
  - Tối ưu đường chạy mũi khoan bản mạch in điện tử (PCB CNC drilling).
  - Lập trình tự gia công trên máy đơn và giải trình tự gen (ADN sequencing).
- **Mô hình Quy hoạch nguyên tuyến tính (ILP):**
  $$\min \sum_{i=1}^n \sum_{j \neq i} d_{ij} x_{ij} \quad \text{s.t.} \quad \sum_{j \neq i} x_{ij} = 1, \; \sum_{i \neq j} x_{ij} = 1, \; \sum_{i, j \in S} x_{ij} \le |S| - 1 \; (\forall S \subset V)$$

---

## Slide 3: Tính NP-khó & Sự bùng nổ không gian tìm kiếm

- **Phiên bản quyết định (`TSP-DECISION`):** Có tồn tại chu trình Hamilton độ dài $\le L$?
- **Chứng minh NP-đầy đủ (Karp, 1972):**
  - Kiểm chứng một chu trình ứng viên tốn $\mathcal{O}(n) \Rightarrow \text{TSP-DECISION} \in \text{NP}$.
  - Quy dẫn đa thức $\text{HAMILTONIAN-CYCLE} \le_p \text{TSP-DECISION}$: Gán $d_{ij} = 1$ nếu $(i,j) \in E(G')$, $d_{ij} = 2$ nếu $(i,j) \notin E(G')$, và đặt $L = n$.
- **Kích thước không gian tìm kiếm (TSP đối xứng):** $|\Omega| = \frac{(n-1)!}{2}$
  - $n = 10 \Rightarrow 181\,440$ chu trình.
  - $n = 20 \Rightarrow 6.08 \times 10^{16}$ chu trình.
  - $n = 52$ (`berlin52`) $\Rightarrow 7.75 \times 10^{65}$ chu trình (vét cạn mất $> 10^{49}$ năm!).

---

## Slide 4: Thuật toán chính xác (Held–Karp & Nhánh cận)

1. **Quy hoạch động trạng thái bitmask Held–Karp $\mathcal{O}(n^2 2^n)$:**
   $$DP[S][u] = \min_{w \in S \setminus \{u\}} \big\{ DP[S \setminus \{u\}][w] + d_{w,u} \big\}$$
   - Tối ưu hóa bộ nhớ trong Python bằng mảng phẳng `bytearray` cho bảng truy vết `parent` và chỉ giữ 2 lớp DP liên tiếp bằng `array('d')`.
2. **Nhánh cận (Branch and Bound) với cận dưới 2-cạnh ngắn nhất:**
   $$LB = \text{cost}(\text{path}) + \frac{1}{2}\sum_{w \notin \text{path}} (e_{w,1} + e_{w,2}) + \frac{1}{2}(e_{\text{last},1} + e_{0,1})$$
   - Khớp 100% nghiệm tối ưu với Held–Karp và Vét cạn trên mọi bộ dữ liệu nhỏ.

---

## Slide 5: Heuristic xây dựng & Tìm kiếm cục bộ (Delta $\mathcal{O}(1)$)

- **Heuristic xây dựng (Tham lam):**
  - *Nearest Neighbor (NN)* & *Multi-Start NN*: Chọn đỉnh gần nhất chưa thăm ($\mathcal{O}(n^2)$).
  - *Cheapest Insertion (CI)*: Chèn đỉnh $k$ vào cạnh $(i,j)$ có $\Delta = d_{ik} + d_{kj} - d_{ij}$ nhỏ nhất ($\mathcal{O}(n^3)$ trường hợp xấu nhất, tối ưu hóa thực nghiệm nhờ lưu đệm vị trí chèn).
- **Tìm kiếm cục bộ (3 cấu trúc lân cận — First & Best Improvement):**
  1. **`2-opt` (Đảo đoạn):** $\Delta = (d_{a,c} + d_{b,d}) - (d_{a,b} + d_{c,d})$ — đánh giá trong $\mathcal{O}(1)$.
  2. **`Swap` (Đổi chỗ 2 đỉnh):** Đánh giá sự thay đổi của 4 cạnh kề trong $\mathcal{O}(1)$.
  3. **`Or-opt` (Dịch chuyển đoạn 1–3 đỉnh):** Đánh giá 3 cạnh cắt/nối trong $\mathcal{O}(1)$.

---

## Slide 6: Bốn giải thuật Metaheuristic & Thuật toán Lai

1. **Simulated Annealing (SA - Thành viên 1):** Đơn lời giải; lân cận 2-opt/Swap, nhận nghiệm xấu với xác suất $e^{-\Delta/T}$, làm nguội $T_{k+1} = \alpha T_k$ + Reheating.
2. **Tabu Search (TS - Thành viên 2):** Đơn lời giải; danh sách cấm cạnh vừa cắt trong $\theta = \lfloor 2.5\sqrt{n}\rfloor$ vòng, có tiêu chí mong đợi (*Aspiration Criterion*).
3. **Genetic Algorithm (GA - Thành viên 3):** Quần thể; mã hóa hoán vị, lai ghép thứ tự **OX** & **PMX** (bảo toàn hoán vị hợp lệ 100%), đột biến đảo đoạn, giữ ưu tú (*Elitism*).
4. **Ant Colony Optimization (ACO - Thành viên 4):** Quần thể; xây dựng chu trình theo $[\tau_{ij}]^\alpha [\eta_{ij}]^\beta$ trên *Candidate List*, cập nhật mùi giới hạn $[\tau_{\min}, \tau_{\max}]$ (MMAS).
5. **Memetic Algorithm (Thuật toán Lai):** Kết hợp lai ghép `OX` của GA + tìm kiếm cục bộ `2-opt` trên từng cá thể con + nhiễu **4-opt Double-Bridge**.

---

## Slide 7: Kết quả thực nghiệm & Kiểm định thống kê

- **600 lần chạy độc lập** (12 thể hiện $\times$ 5 thuật toán $\times$ 10 seeds, cùng ngân sách thời gian):
  - Trên 5 thể hiện nhỏ ($n=10..18$): `SA`, `TS`, `ACO`, `Memetic` đạt **100% nghiệm tối ưu** của Held–Karp.
  - Trên 5 bộ chuẩn TSPLIB (`eil51`, `berlin52`, `st70`, `eil76`, `kroA100`): **Memetic** và **ACO** đạt chính xác **100% giá trị BKS ($\text{Best Gap} = 0.000\%$)**.
- **Kiểm định Friedman ($N=12, df=4$):** $p < 0.0001$, hạng trung bình tốt nhất thuộc về **Memetic** và **ACO**.
- **Kiểm định Wilcoxon chính xác (Exact Signed-Rank Test):** Khẳng định sự cải thiện có ý nghĩa thống kê ($p < 0.05$).
- **Mở rộng $n = 1000$:** 2-opt với *Candidate List* ($k=20$) hội tụ trong $0.002\text{s}$.

---

## Slide 8: Demo Chương trình Trực quan hóa

- **Demo 1:** Giao diện Web Dashboard tương tác thời gian thực (`visualizer/index.html`)
  - Chạy trực tiếp `Nearest Neighbor`, `Cheapest Insertion`, `2-opt`, `SA`, `TS`, `GA`, `ACO`, `Memetic` trên `berlin52` và `kroA100`.
- **Demo 2:** Giao diện Python Tkinter GUI (`python gui_visualizer.py`) & Hàm kiểm tra tính hợp lệ độc lập (`validator.py`).
- **Cảm ơn Thầy/Cô và các bạn đã lắng nghe! Nhóm xin phép bước vào phần Demo và Vấn đáp.**
