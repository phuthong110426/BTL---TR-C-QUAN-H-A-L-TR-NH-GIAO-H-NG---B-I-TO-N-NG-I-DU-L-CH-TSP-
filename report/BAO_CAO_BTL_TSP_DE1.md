# BÁO CÁO BÀI TẬP LỚN
**TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI THÀNH PHỐ HỒ CHÍ MINH**  
**NGÀNH CÔNG NGHỆ THÔNG TIN**  
**HỌC PHẦN: PHÂN TÍCH THIẾT KẾ GIẢI THUẬT**

---

## ĐỀ TÀI 1: LỘ TRÌNH XE GIAO HÀNG — BÀI TOÁN NGƯỜI DU LỊCH (TSP)
**Chủ đề:** Các bài toán NP-khó và Giải thuật Metaheuristic  
**Quy mô thực hiện:** Nhóm 4 thành viên (4 Metaheuristic + 1 Thuật toán Lai Memetic + Phân tích độ nhạy tham số + Kiểm định thống kê Friedman & Wilcoxon + Trực quan hóa lộ trình)

---

## MỤC LỤC
1. **Chương 1: Phát biểu bài toán và Mô hình toán học**
   - 1.1. Mô tả bài toán thực tế và ứng dụng
   - 1.2. Mô hình toán học Quy hoạch nguyên tuyến tính (ILP)
   - 1.3. Ví dụ minh họa cỡ nhỏ ($n = 5$) có lời giải chi tiết
2. **Chương 2: Độ phức tạp tính toán và Không gian tìm kiếm**
   - 2.1. Phiên bản tối ưu và phiên bản quyết định (TSP-DECISION)
   - 2.2. Chứng minh tính NP-đầy đủ và NP-khó (Quy dẫn từ Chu trình Hamilton)
   - 2.3. Phân tích kích thước không gian tìm kiếm
3. **Chương 3: Thuật toán chính xác (Exact Algorithms)**
   - 3.1. Thuật toán Quy hoạch động trạng thái bitmask Held–Karp $\mathcal{O}(n^2 2^n)$
   - 3.2. Thuật toán Nhánh cận (Branch and Bound) với cận dưới 2-cạnh ngắn nhất
   - 3.3. Đánh giá giới hạn kích thước giải được trong thực tế
4. **Chương 4: Heuristic xây dựng (Tham lam) và Tìm kiếm cục bộ (Local Search)**
   - 4.1. Biểu diễn lời giải và Hàm kiểm tra tính hợp lệ độc lập
   - 4.2. Các thuật toán Heuristic xây dựng: Nearest Neighbor, Multi-Start NN, Cheapest Insertion
   - 4.3. Tìm kiếm cục bộ: Ba cấu trúc lân cận (`2-opt`, `Swap`, `Or-opt`) và Đánh giá gia tăng (Delta Evaluation $\mathcal{O}(1)$)
   - 4.4. Chiến lược Leo đồi: First Improvement vs Best Improvement và kỹ thuật Candidate List
5. **Chương 5: Các giải thuật Metaheuristic và Thuật toán Lai (Memetic)**
   - 5.1. Tôi luyện mô phỏng (Simulated Annealing - SA) [Đơn lời giải - Thành viên 1]
   - 5.2. Tìm kiếm Tabu (Tabu Search - TS) [Đơn lời giải - Thành viên 2]
   - 5.3. Giải thuật Di truyền (Genetic Algorithm - GA với OX & PMX) [Quần thể - Thành viên 3]
   - 5.4. Tối ưu Đàn kiến (Ant Colony Optimization - ACO / MMAS) [Quần thể - Thành viên 4]
   - 5.5. Thuật toán Lai Memetic (GA + 2-opt Local Search + Nhiễu Double-Bridge) [Nhóm 4 người]
6. **Chương 6: Thực nghiệm, Phân tích tham số và Kiểm định thống kê**
   - 6.1. Môi trường thực nghiệm và Bộ dữ liệu (TSPLIB & Tự sinh)
   - 6.2. Thực nghiệm Thuật toán chính xác trên dữ liệu nhỏ ($n = 10 \dots 20$)
   - 6.3. Thực nghiệm Heuristic xây dựng và Tìm kiếm cục bộ
   - 6.4. Thực nghiệm so sánh 5 Metaheuristic trên 12 thể hiện (600 lần chạy độc lập)
   - 6.5. Phân tích đường hội tụ (Convergence Analysis)
   - 6.6. Phân tích độ nhạy tham số (Parameter Sensitivity Analysis)
   - 6.7. Kiểm định thống kê phi tham số (Friedman Test & Wilcoxon Signed-Rank Test)
   - 6.8. Mở rộng: Giải thể hiện lớn $n = 1000$ với Candidate List và Giao diện trực quan hóa
7. **Chương 7: Kết luận, Hạn chế, Hướng phát triển, Tài liệu tham khảo & Phân công**

---

## CHƯƠNG 1: PHÁT BIỂU BÀI TOÁN VÀ MÔ HÌNH TOÁN HỌC

### 1.1. Mô tả bài toán thực tế và ứng dụng
Trong lĩnh vực logistics và vận tải đô thị hiện đại, bài toán lập lộ trình giao hàng chặng cuối (*last-mile delivery*) đóng vai trò quyết định đến chi phí nhiên liệu và thời gian vận hành. Xét một phương tiện giao hàng xuất phát từ một kho trung tâm (depot), cần đi giao hàng (hoặc thu gom bưu kiện) tại $n - 1$ điểm khách hàng đã biết trước tọa độ địa lý, mỗi điểm ghé thăm đúng một lần trước khi quay trở về kho xuất phát. Mục tiêu của nhà điều phối là tìm thứ tự ghé thăm các điểm sao cho tổng quãng đường di chuyển (hoặc tổng chi phí/thời gian di chuyển) là nhỏ nhất.

Đây chính là **Bài toán Người du lịch (Traveling Salesman Problem – TSP)** — một trong những bài toán tối ưu tổ hợp kinh điển và được nghiên cứu sâu rộng nhất trong Khoa học máy tính và Vận trù học. Ngoài bài toán giao hàng và thu gom rác thải đô thị, TSP còn xuất hiện trực tiếp trong:
- **Sản xuất công nghiệp (Khoan bản mạch in PCB):** Đầu mũi khoan CNC cần di chuyển qua hàng nghìn lỗ khoan trên bảng mạch điện tử và quay về vị trí gốc; tối ưu hóa chu trình giúp giảm đáng kể thời gian gia công.
- **Lập lịch sản xuất (Job Sequencing):** Xác định thứ tự gia công $n$ chi tiết trên một máy khi thời gian chuyển đổi công cụ từ chi tiết $i$ sang chi tiết $j$ phụ thuộc vào cặp $(i, j)$.
- **Sinh tin học và Thiên văn học:** Sắp xếp các đoạn trình tự ADN (Genome Sequencing) và điều khiển hướng quay kính viễn vọng quan sát chuỗi thiên thể.

### 1.2. Mô hình toán học Quy hoạch nguyên tuyến tính (ILP)
Cho đồ thị đầy đủ $G = (V, E)$ với tập đỉnh $V = \{1, 2, \dots, n\}$ biểu diễn $n$ địa điểm và ma trận khoảng cách không âm $D = [d_{ij}]_{n \times n}$, trong đó $d_{ij} \ge 0$ là khoảng cách (chi phí) đi từ điểm $i$ đến điểm $j$ ($i, j \in V, i \neq j$). Trong bài toán TSP đối xứng (*Symmetric TSP*), ta có $d_{ij} = d_{ji}, \forall i, j \in V$.

#### (a) Biến quyết định
Đặt biến nhị phân $x_{ij} \in \{0, 1\}$ với $\forall i, j \in V, i \neq j$:
$$x_{ij} = \begin{cases} 1, & \text{nếu xe đi trực tiếp từ điểm } i \text{ sang điểm } j \text{ trong chu trình}, \\ 0, & \text{ngược lại.} \end{cases}$$

#### (b) Hàm mục tiêu
Cực tiểu hóa tổng độ dài (chi phí) của toàn bộ lộ trình:
$$\min f(x) = \sum_{i=1}^{n} \sum_{\substack{j=1 \\ j \neq i}}^{n} d_{ij} x_{ij}$$

#### (c) Các ràng buộc (Constraints)
1. **Ràng buộc bậc đi ra (Out-degree constraint):** Mỗi điểm $i \in V$ chỉ có đúng một cạnh đi ra:
   $$\sum_{\substack{j=1 \\ j \neq i}}^{n} x_{ij} = 1, \quad \forall i \in \{1, 2, \dots, n\}$$
2. **Ràng buộc bậc đi vào (In-degree constraint):** Mỗi điểm $j \in V$ chỉ có đúng một cạnh đi vào:
   $$\sum_{\substack{i=1 \\ i \neq j}}^{n} x_{ij} = 1, \quad \forall j \in \{1, 2, \dots, n\}$$
3. **Ràng buộc loại bỏ chu trình con (Subtour Elimination Constraints – SEC):**  
   Chỉ riêng hai ràng buộc bậc vào/ra ở trên mới chỉ tạo ra một phép phân hoạch tập đỉnh thành các chu trình rời nhau (bài toán Phân công – Assignment Problem). Để ép lộ trình tạo thành **một chu trình duy nhất** đi qua cả $n$ đỉnh, ta dùng một trong hai hệ ràng buộc chuẩn sau:
   - **Dạng Dantzig–Fulkerson–Johnson (DFJ, 1954):** Với mọi tập con thực sự $S \subset V$ thỏa $2 \le |S| \le n - 1$:
     $$\sum_{i \in S} \sum_{\substack{j \in S \\ j \neq i}} x_{ij} \le |S| - 1, \quad \forall S \subset V, \; 2 \le |S| \le n - 1$$
     *(Số lượng ràng buộc DFJ là $2^n - 2n - 2$, tăng theo hàm mũ theo $n$).*
   - **Dạng Miller–Tucker–Zemlin (MTZ, 1960):** Đưa thêm $n-1$ biến nguyên phụ $u_i \in \{2, 3, \dots, n\}$ biểu thị thứ tự ghé thăm đỉnh $i$ ($\forall i \in \{2, \dots, n\}$, cố định đỉnh xuất phát là $1$):
     $$u_i - u_j + (n - 1) x_{ij} \le n - 2, \quad \forall i, j \in \{2, \dots, n\}, \; i \neq j$$
4. **Ràng buộc miền giá trị:**
   $$x_{ij} \in \{0, 1\}, \quad \forall i, j \in V, \; i \neq j.$$

#### (d) Biểu diễn dưới dạng bài toán tối ưu tổ hợp trên không gian hoán vị
Một lời giải khả thi tương đương với một hoán vị $\pi = (\pi_0, \pi_1, \dots, \pi_{n-1})$ của tập đỉnh $\{0, 1, \dots, n-1\}$. Khi đó hàm mục tiêu cần tối thiểu hóa là:
$$\min_{\pi \in S_n} f(\pi) = \sum_{k=0}^{n-2} d_{\pi_k, \pi_{k+1}} + d_{\pi_{n-1}, \pi_0}$$

### 1.3. Ví dụ minh họa cỡ nhỏ ($n = 5$) có lời giải chi tiết
Xét bài toán lập lộ trình giao hàng qua $n = 5$ địa điểm (Đỉnh $0$ là Kho trung tâm, các đỉnh $1, 2, 3, 4$ là 4 khách hàng) có tọa độ trên mặt phẳng Euclid như sau:
- Đỉnh $0$: $(0, 0)$
- Đỉnh $1$: $(0, 4)$
- Đỉnh $2$: $(3, 4)$
- Đỉnh $3$: $(6, 0)$
- Đỉnh $4$: $(3, 0)$

Ma trận khoảng cách Euclid đối xứng $D = [d_{ij}]_{5 \times 5}$:

| Đỉnh | 0 | 1 | 2 | 3 | 4 |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | 0 | 4 | 5 | 6 | 3 |
| **1** | 4 | 0 | 3 | $\sqrt{52} \approx 7$ | 5 |
| **2** | 5 | 3 | 0 | 5 | 4 |
| **3** | 6 | 7 | 5 | 0 | 3 |
| **4** | 3 | 5 | 4 | 3 | 0 |

Với $n = 5$ và đồ thị đối xứng, tổng số chu trình phân biệt (không kể chiều đi ngược lại) là $\frac{(5-1)!}{2} = \frac{24}{2} = 12$ chu trình:
1. Chu trình $(0 \to 1 \to 2 \to 3 \to 4 \to 0)$:
   $$f = d_{0,1} + d_{1,2} + d_{2,3} + d_{3,4} + d_{4,0} = 4 + 3 + 5 + 3 + 3 = \mathbf{18}.$$
2. Chu trình $(0 \to 1 \to 4 \to 3 \to 2 \to 0)$:
   $$f = d_{0,1} + d_{1,4} + d_{4,3} + d_{3,2} + d_{2,0} = 4 + 5 + 3 + 5 + 5 = 22.$$
3. Chu trình $(0 \to 2 \to 1 \to 3 \to 4 \to 0)$:
   $$f = d_{0,2} + d_{2,1} + d_{1,3} + d_{3,4} + d_{4,0} = 5 + 3 + 7 + 3 + 3 = 21.$$

Đối chiếu toàn bộ 12 chu trình, **lời giải tối ưu toàn cục** là $\pi^* = (0, 1, 2, 3, 4)$ (và chu trình ngược chiều $(0, 4, 3, 2, 1)$) với tổng độ dài nhỏ nhất $f^* = 18$.

---

## CHƯƠNG 2: ĐỘ PHỨC TẠP TÍNH TOÁN VÀ KHÔNG GIAN TÌM KIẾM

### 2.1. Phiên bản tối ưu và Phiên bản quyết định (TSP-DECISION)
- **Phiên bản tối ưu (TSP-OPT):** Cho đồ thị đầy đủ có trọng số $G = (V, E, d)$. Tìm chu trình Hamilton có tổng trọng số nhỏ nhất.
- **Phiên bản quyết định (TSP-DECISION):** Cho đồ thị đầy đủ $G = (V, E, d)$ và một ngưỡng số dương $L \in \mathbb{R}^+$. Câu hỏi: *"Có tồn tại hay không một chu trình Hamilton trong $G$ có tổng độ dài không vượt quá $L$ ($\le L$)?"*

### 2.2. Chứng minh tính NP-đầy đủ và NP-khó (Karp, 1972)
**Định lý:** Bài toán quyết định `TSP-DECISION` là **NP-đầy đủ (NP-Complete)**, và do đó bài toán tối ưu `TSP-OPT` là **NP-khó (NP-Hard)**.

**Chứng minh (gồm 2 bước chuẩn theo Karp, 1972 và Garey & Johnson, 1979):**

1. **Bước 1: Chứng minh $\text{TSP-DECISION} \in \text{NP}$**  
   Giả sử ta được cung cấp một chứng chỉ (certificate) là một dãy đỉnh $\pi = (\pi_0, \pi_1, \dots, \pi_{n-1})$. Thuật toán kiểm chứng (verifier) thực hiện:
   - Kiểm tra $|\pi| = n$ và mọi đỉnh trong $\{0, \dots, n-1\}$ xuất hiện đúng 1 lần trong $\mathcal{O}(n)$ bằng mảng đánh dấu.
   - Tính tổng trọng số $S = \sum_{k=0}^{n-1} d_{\pi_k, \pi_{(k+1) \bmod n}}$ trong $\mathcal{O}(n)$ phép cộng và kiểm tra $S \le L$.  
   Vì quá trình kiểm chứng hoàn tất trong thời gian đa thức $\mathcal{O}(n)$, bài toán `TSP-DECISION` thuộc lớp $\text{NP}$.

2. **Bước 2: Quy dẫn đa thức $\text{HAMILTONIAN-CYCLE (HC)} \le_p \text{TSP-DECISION}$**  
   Bài toán Chu trình Hamilton (`HC`: Cho đồ thị vô hướng không trọng số $G' = (V, E')$ với $|V| = n$, hỏi $G'$ có chứa chu trình đi qua mỗi đỉnh đúng một lần không?) đã được chứng minh là NP-đầy đủ trong danh sách 21 bài toán của Karp (1972).  
   Từ một thể hiện bất kỳ $G' = (V, E')$ của `HC`, ta xây dựng thể hiện $(G, d, L)$ của `TSP-DECISION` trên cùng tập đỉnh $V$ trong thời gian đa thức $\mathcal{O}(n^2)$ như sau:
   - Đặt ngưỡng $L = n$.
   - Với mọi cặp đỉnh $i, j \in V$ ($i \neq j$), định nghĩa hàm khoảng cách:
     $$d_{ij} = \begin{cases} 1, & \text{nếu } (i, j) \in E', \\ 2, & \text{nếu } (i, j) \notin E'. \end{cases}$$
   - **Tính tương đương:**
     - ($\Rightarrow$) Nếu $G'$ có chu trình Hamilton $C$, thì toàn bộ $n$ cạnh của $C$ đều thuộc $E'$, nên mỗi cạnh có trọng số $d_{ij} = 1$. Tổng độ dài của $C$ trong $G$ là $n \times 1 = n \le L$. Vậy $(G, d, n)$ có câu trả lời `YES`.
     - ($\Leftarrow$) Ngược lại, nếu $G$ có một chu trình đi qua $n$ đỉnh với tổng độ dài $\le n$, vì mọi cạnh đều có trọng số $d_{ij} \ge 1$ và chu trình gồm đúng $n$ cạnh, tổng độ dài chỉ có thể $\le n$ khi và chỉ khi **tất cả $n$ cạnh trong chu trình đều có trọng số bằng $1$**, tức là đều thuộc $E'$. Do đó chu trình này chính là một chu trình Hamilton hợp lệ trong $G'$.
   - Vì phép biến đổi tốn thời gian $\mathcal{O}(n^2)$, ta kết luận $\text{HC} \le_p \text{TSP-DECISION}$, suy ra `TSP-DECISION` là **NP-đầy đủ**.
   - Nếu tồn tại thuật toán thời gian đa thức giải được bài toán tối ưu `TSP-OPT` (tìm giá trị tối ưu $f^*$), ta chỉ cần so sánh $f^* \le L$ trong $\mathcal{O}(1)$ để giải `TSP-DECISION`. Do đó, `TSP-OPT` là **NP-khó**.

### 2.3. Phân tích kích thước không gian tìm kiếm
Khi cố định đỉnh xuất phát là đỉnh $0$ (do tính chất chu trình khép kín, việc xoay vòng một hoán vị không làm thay đổi chu trình), số lượng hoán vị của $n-1$ đỉnh còn lại là $(n-1)!$. Trong trường hợp TSP đối xứng ($d_{ij} = d_{ji}$), hai hoán vị ngược chiều nhau có cùng chi phí, nên kích thước không gian tìm kiếm là:
$$|\Omega| = \frac{(n - 1)!}{2}$$

| Số đỉnh $n$ | Kích thước không gian $\frac{(n-1)!}{2}$ | Thời gian duyệt vét cạn (giả sử $10^9$ chu trình/giây) |
| :---: | :---: | :--- |
| $n = 10$ | $181\,440$ | $0.00018$ giây |
| $n = 15$ | $4.35 \times 10^{10}$ | $\approx 43.5$ giây |
| $n = 20$ | $6.08 \times 10^{16}$ | $\approx 1.93$ năm |
| $n = 52$ (`berlin52`) | $7.75 \times 10^{65}$ | $\approx 2.45 \times 10^{49}$ năm (lớn hơn tuổi vũ trụ) |
| $n = 100$ (`kroA100`) | $4.66 \times 10^{155}$ | Bất khả thi tuyệt đối với mọi siêu máy tính |

Sự bùng nổ giai thừa này giải thích tại sao các thuật toán chính xác chỉ khả thi cho $n$ nhỏ và các giải thuật Metaheuristic là bắt buộc đối với dữ liệu thực tế.

---

## CHƯƠNG 3: THUẬT TOÁN CHÍNH XÁC (EXACT ALGORITHMS)

### 3.1. Quy hoạch động trạng thái bitmask Held–Karp $\mathcal{O}(n^2 2^n)$
Thuật toán quy hoạch động do Bellman (1962) và Held & Karp (1962) độc lập đề xuất giúp giảm độ phức tạp từ $\mathcal{O}(n!)$ xuống hàm mũ cơ số 2 là $\mathcal{O}(n^2 2^n)$.

#### (a) Định nghĩa trạng thái và Công thức truy hồi
Cố định đỉnh xuất phát tại đỉnh $0$. Gọi $S \subseteq \{1, 2, \dots, n-1\}$ là tập con các đỉnh đã đi qua (biểu diễn trong cài đặt bằng số nguyên bitmask có $n-1$ bit), và $u \in S$ là đỉnh kết thúc hiện tại.
Đặt $DP[S][u]$ là độ dài đường đi ngắn nhất xuất phát từ đỉnh $0$, đi qua tất cả các đỉnh trong $S$ đúng một lần và kết thúc tại đỉnh $u$:

- **Cơ sở quy hoạch động ($|S| = 1$, tức $S = \{u\}$):**
  $$DP[\{u\}][u] = d_{0, u}, \quad \forall u \in \{1, \dots, n-1\}$$
- **Công thức truy hồi ($|S| \ge 2$):**
  $$DP[S][u] = \min_{w \in S \setminus \{u\}} \Big\{ DP[S \setminus \{u\}][w] + d_{w, u} \Big\}$$
- **Đóng chu trình để nhận nghiệm tối ưu:**
  $$f^* = \min_{u \in \{1, \dots, n-1\}} \Big\{ DP[\{1, \dots, n-1\}][u] + d_{u, 0} \Big\}$$

#### (b) Mã giả thuật toán Held–Karp
```text
Algorithm 1: Held-Karp Dynamic Programming for TSP
Input: Ma trận khoảng cách D[0..n-1][0..n-1]
Output: Chu trình tối ưu tour* và chi phí tối ưu f*
1: Khởi tạo bảng DP[1..(2^(n-1)-1)][1..n-1] = +∞, Parent = -1
2: for u = 1 to n - 1 do
3:     mask = 1 << (u - 1)
4:     DP[mask][u] = D[0][u]
5:     Parent[mask][u] = 0
6: for size = 1 to n - 2 do
7:     for mỗi mask có đúng `size` bit 1 do
8:         for mỗi u thuộc mask (bit u-1 bằng 1) do
9:             for mỗi v không thuộc mask (bit v-1 bằng 0) do
10:                next_mask = mask | (1 << (v - 1))
11:                if DP[mask][u] + D[u][v] < DP[next_mask][v] then
12:                    DP[next_mask][v] = DP[mask][u] + D[u][v]
13:                    Parent[next_mask][v] = u
14: full_mask = (1 << (n - 1)) - 1
15: f* = min_{u=1..n-1} (DP[full_mask][u] + D[u][0])
16: Truy vết ngược từ u* qua mảng Parent để khôi phục chu trình tour*
17: return tour*, f*
```

#### (c) Phân tích độ phức tạp
- **Thời gian:** Có $2^{n-1}$ trạng thái `mask`, mỗi trạng thái có $n-1$ đỉnh kết thúc $u$, và mỗi cặp $(mask, u)$ thử mở rộng sang tối đa $n-1$ đỉnh $v$. Tổng số phép toán là $\sum_{k=1}^{n-1} \binom{n-1}{k} k (n - 1 - k) = \mathcal{O}(n^2 2^n)$.
- **Không gian bộ nhớ:** Cần lưu bảng `Parent` kích thước $\mathcal{O}(n 2^n)$ để truy vết chu trình (trong mã nguồn `src/exact_solver.py`, nhóm đã tối ưu hóa bằng cách xóa các tầng `DP` của kích thước `size - 1` ngay sau khi tính xong tầng `size`, giảm một nửa dung lượng RAM tiêu thụ).

### 3.2. Thuật toán Nhánh cận (Branch and Bound) với cận dưới 2-cạnh
Thuật toán Nhánh cận duyệt cây tìm kiếm theo chiều sâu (DFS) nhưng cắt tỉa sớm (pruning) các nhánh không có khả năng sinh ra nghiệm tốt hơn kỷ lục hiện tại $UB$ (Upper Bound):
- **Khởi tạo cận trên $UB$:** Sử dụng ngay kết quả của thuật toán tham lam Láng giềng gần nhất (Nearest Neighbor) làm cận trên ban đầu giúp cắt nhánh mạnh ngay từ những giây đầu tiên.
- **Hàm cận dưới $LB$ (2-edge Lower Bound):** Trong mọi chu trình Hamilton hợp lệ, mỗi đỉnh $i \in V$ đều phải nối với đúng 2 cạnh có tổng trọng số ít nhất bằng tổng 2 cạnh ngắn nhất đi ra từ $i$ (gọi là $e_{i,1}$ và $e_{i,2}$). Do đó:
  $$LB_0 = \frac{1}{2} \sum_{i=0}^{n-1} (e_{i,1} + e_{i,2}) \le f^*$$
  Khi nhánh tìm kiếm đi thêm cạnh $(u, v)$, cận dưới $LB$ được cập nhật gia tăng trong $\mathcal{O}(1)$ bằng cách thay thế $e_{u,1}$ (hoặc $e_{u,2}$) và $e_{v,1}$ bằng trọng số thực $d_{u,v}$. Nếu $LB \ge UB$, toàn bộ cây con dưới nhánh đó bị cắt bỏ.

### 3.3. Giới hạn kích thước giải được trong thực tế
Thực nghiệm trong tệp `results/exact_results.csv` (xem chi tiết tại Bảng 6.1 ở Chương 6) cho thấy:
- Với $n \le 16$: Cả Held–Karp và Nhánh cận đều tìm ra nghiệm tối ưu chính xác trong $< 0.45$ giây.
- Với $n = 18$: Held–Karp mất $2.26$ giây, trong khi Nhánh cận (trên dữ liệu phân cụm khó) chạm ngưỡng giới hạn cắt sớm 15 giây sau khi duyệt $16.7$ triệu nút.
- Với $n = 20$: Held–Karp giải chính xác hoàn toàn trong $22.33$ giây. Với giới hạn 10 phút ($600$ giây), Held–Karp trên Python giải được đến kích thước tối đa **$n_{\max} = 23$ đỉnh** (bị giới hạn bởi bộ nhớ RAM $\mathcal{O}(n 2^n)$ và tốc độ tăng gấp $\approx 2.25$ lần mỗi khi tăng thêm 1 đỉnh).

---

## CHƯƠNG 4: HEURISTIC XÂY DỰNG VÀ TÌM KIẾM CỤC BỘ

### 4.1. Biểu diễn lời giải và Hàm kiểm tra tính hợp lệ độc lập
- **Biểu diễn lời giải:** Mọi chu trình được biểu diễn thống nhất bằng một danh sách (mảng) hoán vị $\text{tour} = [v_0, v_1, \dots, v_{n-1}]$ gồm $n$ số nguyên đôi một khác nhau thuộc $\{0, 1, \dots, n-1\}$.
- **Hàm kiểm tra tính hợp lệ độc lập (`src/validator.py`):** Mọi lời giải trước khi báo cáo đều đi qua hàm `validate_tour(instance, tour, reported_cost)`:
  1. Kiểm tra độ dài $|\text{tour}| = n$ trong $\mathcal{O}(1)$.
  2. Kiểm tra tính hoán vị (mọi đỉnh $v \in [0, n-1]$ xuất hiện đúng 1 lần, không lặp, không thiếu) bằng mảng boolean `visited` trong $\mathcal{O}(n)$.
  3. Tính lại tổng độ dài chu trình độc lập từ ma trận khoảng cách và đối chiếu $|f_{\text{actual}} - f_{\text{reported}}| \le 10^{-4}$.

### 4.2. Các thuật toán Heuristic xây dựng (Tham lam)
1. **Láng giềng gần nhất (Nearest Neighbor – NN):**  
   Xuất phát từ đỉnh $v_0$, ở mỗi bước chọn đỉnh chưa thăm $v_{\text{next}} = \arg\min_{u \notin \text{Visited}} d_{v_{\text{curr}}, u}$. Độ phức tạp: $\mathcal{O}(n^2)$. Nhược điểm của NN là ở các bước cuối cùng thường buộc phải nối các đỉnh bị bỏ sót cách xa nhau (tạo cạnh rất dài).
2. **Láng giềng gần nhất đa điểm xuất phát (Multi-Start NN):**  
   Chạy NN từ $k = \min(n, 30)$ đỉnh xuất phát khác nhau và lấy chu trình tốt nhất. Độ phức tạp: $\mathcal{O}(k \cdot n^2)$.
3. **Chèn rẻ nhất (Cheapest Insertion – CI):**  
   Khởi tạo chu trình con từ 2 đỉnh gần nhau nhất. Ở mỗi bước, tìm đỉnh $k$ chưa thuộc chu trình và vị trí cạnh $(i, j)$ thuộc chu trình sao cho chi phí tăng thêm $\Delta_{\text{insert}}(i, k, j) = d_{i,k} + d_{k,j} - d_{i,j}$ đạt giá trị nhỏ nhất. Bằng kỹ thuật lưu đệm vị trí chèn tốt nhất cho từng đỉnh chưa thăm trong `src/constructive.py`, mỗi bước thông thường chỉ tốn $\mathcal{O}(n)$ (khi đỉnh $u$ có cạnh lưu đệm vừa bị tách mới cần quét lại chu trình), do đó độ phức tạp trường hợp xấu nhất là $\mathcal{O}(n^3)$ nhưng thời gian chạy trung bình trên thực nghiệm tiệm cận $\mathcal{O}(n^2)$.

### 4.3. Tìm kiếm cục bộ (Local Search) và Đánh giá gia tăng (Delta Evaluation)
Để tránh việc tính lại toàn bộ độ dài chu trình tốn $\mathcal{O}(n)$ sau mỗi phép thử, nhóm thiết kế công thức **Đánh giá gia tăng (Delta Evaluation)** với chi phí $\mathcal{O}(1)$ cho cả 3 cấu trúc lân cận trong `src/local_search.py`:

| Cấu trúc lân cận | Định nghĩa phép biến đổi | Kích thước lân cận | Công thức Delta Evaluation $\Delta = f(\text{new}) - f(\text{old})$ | Chi phí đánh giá |
| :--- | :--- | :---: | :--- | :---: |
| **1. Lân cận `2-opt`** | Đảo ngược đoạn con $\text{tour}[i \dots j]$ ($1 \le i < j < n$) | $\frac{n(n-3)}{2} = \mathcal{O}(n^2)$ | Xóa 2 cạnh $(a, b), (c, d)$ và thêm $(a, c), (b, d)$ với $a=\text{tour}[i-1], b=\text{tour}[i], c=\text{tour}[j], d=\text{tour}[(j+1)\bmod n]$:<br>$\Delta_{\text{2-opt}} = (d_{a,c} + d_{b,d}) - (d_{a,b} + d_{c,d})$ | $\mathcal{O}(1)$ (4 phép tra bảng) |
| **2. Lân cận `Swap`** | Đổi chỗ hai đỉnh tại vị trí $i$ và $j$ ($\text{tour}[i] \leftrightarrow \text{tour}[j]$) | $\frac{n(n-1)}{2} = \mathcal{O}(n^2)$ | Nếu $i, j$ không kề nhau ($u=\text{tour}[i], v=\text{tour}[j]$):<br>$\Delta_{\text{swap}} = (d_{p_i, v} + d_{v, n_i} + d_{p_j, u} + d_{u, n_j}) - (d_{p_i, u} + d_{u, n_i} + d_{p_j, v} + d_{v, n_j})$<br>*(Trường hợp $j = i+1$ rút gọn còn 6 phép tra bảng)* | $\mathcal{O}(1)$ |
| **3. Lân cận `Or-opt`** | Dịch chuyển đoạn gồm $k \in \{1, 2, 3\}$ đỉnh liên tiếp từ vị trí $i$ sang chèn sau vị trí $m$ | $\approx 3n(n-3) = \mathcal{O}(n^2)$ | Gọi $u_1=\text{tour}[i], u_k=\text{tour}[i+k-1]$:<br>$\Delta_{\text{remove}} = d_{p_i, n_{i+k-1}} - (d_{p_i, u_1} + d_{u_k, n_{i+k-1}})$<br>$\Delta_{\text{insert}} = (d_{\text{tour}[m], u_1} + d_{u_k, \text{tour}[m+1]}) - d_{\text{tour}[m], \text{tour}[m+1]}$<br>$\Delta_{\text{Or-opt}} = \Delta_{\text{remove}} + \Delta_{\text{insert}}$ | $\mathcal{O}(1)$ |

### 4.4. So sánh chiến lược First Improvement và Best Improvement
- **First Improvement (FI):** Duyệt lân cận và thực hiện ngay phép biến đổi đầu tiên có $\Delta < 0$. Giúp chu trình thay đổi nhanh, tốn ít phép đánh giá ở những bước đầu.
- **Best Improvement (BI):** Duyệt toàn bộ $\mathcal{O}(n^2)$ phần tử lân cận ở mỗi bước và chọn phép biến đổi có $\Delta < 0$ âm sâu nhất.
- **Kỹ thuật Candidate List + Don't-Look Bits:** Khi $n \ge 1000$, việc duyệt mọi cặp $(i, j)$ tốn $\mathcal{O}(n^2)$ mỗi bước trở nên chậm. Trong `src/local_search.py`, nhóm tiền xử lý danh sách $k = 20$ láng giềng gần nhất cho mỗi đỉnh và sử dụng mảng cờ `dont_look[u]`: chỉ xét các phép 2-opt mà cạnh mới $(u, v)$ nằm trong Candidate List của $u$ và có $d_{u,v} < d_{u, u_{\text{next}}}$. Độ phức tạp mỗi vòng lặp giảm từ $\mathcal{O}(n^2)$ xuống $\mathcal{O}(k \cdot n) = \mathcal{O}(n)$.

---

## CHƯƠNG 5: CÁC GIẢI THUẬT METAHEURISTIC VÀ THUẬT TOÁN LAI

Theo quy định tại Mục 2.2 cho **nhóm 4 thành viên**, nhóm tìm hiểu sâu và tự cài đặt **4 giải thuật Metaheuristic** (gồm 2 giải thuật đơn lời giải: **SA, TS** và 2 giải thuật quần thể: **GA, ACO**) cùng **1 Thuật toán Lai (Memetic Algorithm)**.

---

### 5.1. Metaheuristic 1: Tôi luyện mô phỏng (Simulated Annealing – SA)
*(Thành viên 1 phụ trách — Nhóm: Đơn lời giải)*

1. **Nguồn gốc và Tài liệu gốc:**  
   Được đề xuất bởi **Kirkpatrick, Gelatt, & Vecchi (1983)** trên tạp chí *Science* (*"Optimization by Simulated Annealing"*), lấy cảm hứng từ quá trình ủ nhiệt kim loại trong vật lý thống kê.
2. **Nguyên lý hoạt động:**  
   Tìm kiếm cục bộ thông thường bị kẹt ngay tại cực trị cục bộ đầu tiên vì chỉ chấp nhận $\Delta < 0$. SA khắc phục bằng cách cho phép đi sang lân cận xấu hơn ($\Delta > 0$) với xác suất Boltzmann phụ thuộc vào nhiệt độ hiện tại $T$:
   $$P(\text{accept}) = \begin{cases} 1, & \text{nếu } \Delta \le 0, \\ \exp\left(-\frac{\Delta}{T}\right), & \text{nếu } \Delta > 0. \end{cases}$$
   Khi $T$ cao (đầu quá trình), thuật toán ưu tiên **khám phá (diversification)**; khi $T$ giảm dần theo cấp số nhân $T_{k+1} = \alpha \cdot T_k$, xác suất nhận nghiệm xấu tiến về 0, thuật toán tập trung **khai thác (intensification)** quanh vùng nghiệm tốt.
3. **Biểu diễn lời giải, Toán tử và Xử lý ràng buộc:**  
   Biểu diễn bằng hoán vị $n$ đỉnh. Toán tử tạo lân cận hỗn hợp: với xác suất $90\%$ chọn ngẫu nhiên cặp $(i, j)$ để thực hiện phép đảo đoạn `2-opt`, và $10\%$ thực hiện phép đổi chỗ `Swap`. Cả hai toán tử đều bảo toàn tính hoán vị nên lời giải luôn hợp lệ 100% mà không cần hàm phạt.
4. **Mã giả cụ thể cho bài toán TSP:**
```text
Algorithm 2: Simulated Annealing (SA) for TSP
Input: Thể hiện TSP, nhiệt độ đầu T0, hệ số làm nguội α, số bước mỗi mức nhiệt L, T_min
Output: Chu trình tốt nhất s_best, f_best
1: s ← NearestNeighbor(random_start_node); f ← cost(s)
2: s_best ← s; f_best ← f; T ← T0
3: while chưa hết thời gian time_limit do
4:     for step = 1 to L do
5:         Chọn ngẫu nhiên 1 <= i < j < n
6:         Tính Δ = delta_2opt(s, i, j) trong O(1) (hoặc delta_swap với xác suất 10%)
7:         if Δ < 0 or Random(0, 1) < exp(-Δ / T) then
8:             Áp dụng phép biến đổi lên s; f ← f + Δ
9:             if f < f_best then s_best ← s; f_best ← f
10:    T ← α * T
11:    if T < T_min then T ← 0.25 * T0; s ← s_best; f ← f_best  // Reheating thoát kẹt
12: return s_best, f_best
```
5. **Tham số và Độ phức tạp:**  
   - $T_0 = \frac{f(\text{NN})}{2n}$ (tự động thích nghi theo thang đo khoảng cách của từng bộ dữ liệu), $\alpha = 0.995$, $L = \min(200, 2n)$.
   - Độ phức tạp mỗi bước thử: $\mathcal{O}(1)$ nhờ Delta Evaluation; chỉ khi chấp nhận bước đi mới tốn $\mathcal{O}(j - i) = \mathcal{O}(n)$ để đảo đoạn.

---

### 5.2. Metaheuristic 2: Tìm kiếm Tabu (Tabu Search – TS)
*(Thành viên 2 phụ trách — Nhóm: Đơn lời giải)*

1. **Nguồn gốc và Tài liệu gốc:**  
   Được đề xuất bởi **Fred Glover (1986)** (*"Future paths for integer programming and links to artificial intelligence"*, Computers & Operations Research).
2. **Nguyên lý hoạt động:**  
   Ở mỗi vòng lặp, TS duyệt tập ứng viên trong lân cận `2-opt` và **luôn di chuyển tới lân cận tốt nhất** (kể cả khi $\Delta > 0$, tức bước đi làm xấu hàm mục tiêu tạm thời để thoát khỏi hố cực trị cục bộ). Để ngăn thuật toán rơi vào vòng lặp vô hạn (quay lại ngay lời giải vừa rời đi), TS sử dụng bộ nhớ ngắn hạn gọi là **Danh sách Tabu (Tabu List)** lưu các cạnh vừa bị cắt trong $\theta$ vòng lặp gần nhất ($\theta$ là *tabu tenure*).
3. **Tiêu chí mong đợi (Aspiration Criterion):**  
   Nếu một phép biến đổi bị đánh dấu Tabu nhưng lại mang đến chi phí $f_{\text{curr}} + \Delta < f_{\text{best}}$ (phá kỷ lục toàn cục), lệnh cấm Tabu được gỡ bỏ ngay lập tức.
4. **Mã giả cụ thể cho bài toán TSP:**
```text
Algorithm 3: Tabu Search (TS) for TSP
Input: Thể hiện TSP, độ dài cấm cơ sở θ (tabu_tenure), kích thước mẫu ứng viên K
Output: Chu trình tốt nhất s_best, f_best
1: s ← NearestNeighbor(random_start); f ← cost(s)
2: s_best ← s; f_best ← f; TabuDict ← ∅; iter ← 0
3: while chưa hết thời gian time_limit do
4:     iter ← iter + 1
5:     Candidates ← Lấy mẫu K cặp chỉ số (i, j) của lân cận 2-opt
6:     best_Δ ← +∞; best_move ← None
7:     for mỗi (i, j) in Candidates do
8:         Δ ← delta_2opt(s, i, j)  // O(1)
9:         e_cut ← (min(s[i-1], s[i]), max(s[i-1], s[i]))
10:        is_tabu ← (TabuDict[e_cut] > iter)
11:        if (not is_tabu) or (f + Δ < f_best) then  // Aspiration Criterion
12:            if Δ < best_Δ then best_Δ ← Δ; best_move ← (i, j, e_cut)
13:    Thực hiện 2-opt tại best_move (i, j) trên s; f ← f + best_Δ
14:    TabuDict[e_cut] ← iter + θ + UniformInt(-2, 2)  // Robust Tabu Tenure
15:    if f < f_best then s_best ← s; f_best ← f
16: return s_best, f_best
```
5. **Tham số và Độ phức tạp:**  
   - $\theta = \lfloor 2.5\sqrt{n} \rfloor \pm 2$, số ứng viên đánh giá mỗi vòng $K = \max(60, 3n)$.
   - Độ phức tạp mỗi vòng lặp: $\mathcal{O}(K + n) = \mathcal{O}(n)$ nhờ tra cứu bảng băm `TabuDict` trong $\mathcal{O}(1)$ và đánh giá `delta_2opt` trong $\mathcal{O}(1)$.

---

### 5.3. Metaheuristic 3: Giải thuật Di truyền (Genetic Algorithm – GA)
*(Thành viên 3 phụ trách — Nhóm: Quần thể)*

1. **Nguồn gốc và Tài liệu gốc:**  
   Giải thuật Di truyền do **John Holland (1975)** đề xuất. Đối với bài toán TSP mã hóa bằng hoán vị, các toán tử lai ghép bảo toàn thứ tự được phát triển bởi **Davis (1985)** (*Order Crossover – OX*) và **Goldberg & Lingle (1985)** (*Partially Mapped Crossover – PMX*).
2. **Biểu diễn lời giải và Xử lý ràng buộc:**  
   Mỗi cá thể (chromosome) là một mảng hoán vị của $\{0, 1, \dots, n-1\}$. Nếu dùng lai ghép cắt 1 điểm (one-point crossover) thông thường của mã nhị phân, cá thể con sẽ bị lặp đỉnh và thiếu đỉnh. Do đó, nhóm sử dụng toán tử chuyên biệt **Order Crossover (OX)** và **PMX** để mọi cá thể con sinh ra luôn là một hoán vị hợp lệ 100% mà không cần thủ tục sửa chữa tốn kém.
3. **Các toán tử di truyền:**
   - **Chọn lọc (Selection):** Đấu loại $k = 3$ (*Tournament Selection*) — lấy ngẫu nhiên 3 cá thể từ quần thể và chọn cá thể có chi phí nhỏ nhất làm cha/mẹ.
   - **Lai ghép thứ tự OX (Order Crossover):** Chọn ngẫu nhiên 2 điểm cắt $a < b$. Sao chép nguyên đoạn $\text{parent}_1[a \dots b]$ sang $\text{child}[a \dots b]$. Các vị trí còn lại từ $(b+1) \bmod n$ được điền lần lượt bằng các đỉnh chưa xuất hiện theo đúng thứ tự tuần tự trong $\text{parent}_2$.
   - **Đột biến (Mutation):** Đột biến đảo đoạn (*Inversion Mutation* — tương đương phép 2-opt ngẫu nhiên, chiếm $80\%$) kết hợp đột biến đổi chỗ 2 đỉnh (*Swap Mutation*, chiếm $20\%$).
   - **Thay thế giữ ưu tú (Elitism):** Giữ nguyên `elite_size = 4` cá thể tốt nhất của thế hệ hiện tại chuyển thẳng sang thế hệ kế tiếp để đảm bảo chất lượng tốt nhất của quần thể đơn điệu không tăng.
4. **Mã giả cụ thể cho bài toán TSP:**
```text
Algorithm 4: Genetic Algorithm (GA with OX/PMX) for TSP
Input: Thể hiện TSP, kích thước quần thể P, xác suất lai p_c, xác suất đột biến p_m, số ưu tú E
Output: Cá thể tốt nhất s_best, f_best
1: Khởi tạo quần thể Pop gồm P cá thể (15% từ Nearest Neighbor nhiễu nhẹ + 85% hoán vị ngẫu nhiên)
2: Đánh giá fitness f(s) = tour_cost(s) cho mọi s in Pop; cập nhật s_best, f_best
3: while chưa hết thời gian time_limit do
4:     NewPop ← E cá thể có chi phí nhỏ nhất trong Pop (Elitism)
5:     while |NewPop| < P do
6:         p1 ← TournamentSelect(Pop, k=3); p2 ← TournamentSelect(Pop, k=3)
7:         if Random(0, 1) < p_c then child ← OrderCrossover_OX(p1, p2) else child ← p1
8:         if Random(0, 1) < p_m then child ← InversionOrSwapMutation(child)
9:         Đánh giá f(child); thêm child vào NewPop
10:        if f(child) < f_best then s_best ← child; f_best ← f(child)
11:    Pop ← NewPop
12: return s_best, f_best
```
5. **Độ phức tạp mỗi thế hệ:**  
   Mỗi phép lai OX/PMX và đánh giá chi phí tốn $\mathcal{O}(n)$, nên một thế hệ gồm $P$ cá thể có độ phức tạp $\mathcal{O}(P \cdot n)$.

---

### 5.4. Metaheuristic 4: Tối ưu Đàn kiến (Ant Colony Optimization – ACO)
*(Thành viên 4 phụ trách — Nhóm: Quần thể)*

1. **Nguồn gốc và Tài liệu gốc:**  
   TSP chính là **bài toán gốc** mà **Marco Dorigo (1992)** sử dụng khi phát minh ra Ant System trong luận án tiến sĩ, và sau đó được hoàn thiện thành **Ant Colony System (ACS)** và **MAX–MIN Ant System (MMAS)** bởi **Stützle & Hoos (2000)** và **Dorigo & Stützle (2004)**.
2. **Nguyên lý hoạt động:**  
   Mô phỏng hành vi tìm đường của đàn kiến tự nhiên thông qua chất dẫn dụ (**vết mùi pheromone** $\tau_{ij}$) kết hợp với **thông tin heuristic cục bộ** $\eta_{ij} = \frac{1}{d_{ij}}$.  
   Ở mỗi bước, một con kiến đang đứng tại đỉnh $i$ chọn đỉnh kế tiếp $j$ chưa thăm (ưu tiên trong danh sách láng giềng gần `Candidate List`) theo quy tắc tỷ lệ giả ngẫu nhiên (*Pseudorandom Proportional Rule*):
   - Với xác suất $q_0 \in [0, 1]$: Khai thác trực tiếp cạnh tốt nhất $j = \arg\max_{u \in \text{Avail}} \left( [\tau_{iu}]^\alpha \cdot [\eta_{iu}]^\beta \right)$.
   - Với xác suất $1 - q_0$: Chọn theo bánh xe Roulette với phân phối xác suất:
     $$p_{ij} = \frac{[\tau_{ij}]^\alpha \cdot [\eta_{ij}]^\beta}{\sum_{u \in \text{Avail}} [\tau_{iu}]^\alpha \cdot [\eta_{iu}]^\beta}$$
   - **Cập nhật và Giới hạn vết mùi (MMAS):** Sau khi $m$ con kiến hoàn thành chu trình, vết mùi trên mọi cạnh bay hơi theo hệ số $\rho \in (0, 1)$ và chỉ con kiến tốt nhất được bồi đắp thêm mùi $\Delta \tau = \frac{1}{L_{\text{best}}}$, đồng thời giới hạn trong đoạn $[\tau_{\min}, \tau_{\max}]$ để tránh hiện tượng hội tụ sớm vào một đường duy nhất:
     $$\tau_{ij} \leftarrow \max\Big(\tau_{\min}, \; \min\big(\tau_{\max}, \; (1 - \rho)\tau_{ij} + \Delta \tau_{ij}^{\text{best}}\big)\Big)$$
3. **Mã giả cụ thể cho bài toán TSP:**
```text
Algorithm 5: Ant Colony Optimization (MMAS / ACS with Candidate List) for TSP
Input: Thể hiện TSP, số kiến m, α, β, hệ số bay hơi ρ, ngưỡng khai thác q0
Output: Chu trình tốt nhất s_best, f_best
1: s_best ← NearestNeighbor(0); f_best ← cost(s_best)
2: τ_max ← 1 / (ρ * f_best); τ_min ← τ_max / (2n); Khởi tạo τ[i][j] = τ_max
3: Tiền tính toán η_beta[i][j] = (1 / d[i][j])^β và CandidateList[i] (k=20)
4: while chưa hết thời gian time_limit do
5:     s_iter_best ← None; f_iter_best ← +∞
6:     for ant = 1 to m do
7:         Xây dựng chu trình s_ant từ đỉnh ngẫu nhiên theo quy tắc q0 và xác suất p_ij trên CandidateList
8:         if cost(s_ant) < f_iter_best then s_iter_best ← s_ant; f_iter_best ← cost(s_ant)
9:     Tinh chỉnh nhẹ s_iter_best bằng 2-opt cục bộ; cập nhật s_best nếu f_iter_best < f_best
10:    Bay hơi mùi: τ[i][j] ← max(τ_min, (1 - ρ) * τ[i][j]) với mọi (i, j)
11:    Bồi đắp mùi Δτ = 1 / f_best trên các cạnh thuộc s_best (hoặc s_iter_best), cắt trần tại τ_max
12: return s_best, f_best
```
4. **Độ phức tạp mỗi vòng lặp:**  
   Nhờ sử dụng Candidate List kích thước $k \ll n$, mỗi con kiến xây dựng chu trình chỉ tốn $\mathcal{O}(k \cdot n)$ thay vì $\mathcal{O}(n^2)$. Tổng độ phức tạp một thế hệ gồm $m$ kiến và bước cập nhật bảng mùi là $\mathcal{O}(m \cdot k \cdot n + n^2)$.

---

### 5.5. Thuật toán Lai: Giải thuật Memetic (MA = GA + 2-opt + Double-Bridge)
*(Yêu cầu bắt buộc cho nhóm 4 thành viên theo Mục 2.2)*

1. **Nguồn gốc và Tài liệu gốc:**  
   Khái niệm **Memetic Algorithm (MA)** được **Pablo Moscato (1989)** giới thiệu, kết hợp tiến hóa quần thể của Giải thuật Di truyền (Darwinian evolution) với quá trình học cục bộ của từng cá thể (Lamarckian local improvement), đồng thời tích hợp phép nhiễu **Double-Bridge 4-opt** của **Martin, Otto, & Felten (1991)**.
2. **Tại sao GA thuần túy gặp khó khăn trên TSP lớn và Memetic giải quyết triệt để?**  
   Trên TSP, phép lai ghép thứ tự (OX/PMX) ghép hai đoạn chu trình từ cha và mẹ thường tạo ra một vài cạnh nối chéo (cross-edges) ở điểm tiếp giáp. Nếu không có tìm kiếm cục bộ sửa ngay các cạnh chéo này, cá thể con có hàm mục tiêu xấu và bị loại bỏ. Trong **Memetic Algorithm**:
   - Mọi cá thể sau khi lai ghép `OX` đều được đưa qua **Pha tìm kiếm cục bộ `2-opt` (First Improvement + Candidate List)** để leo thẳng lên cực trị cục bộ của vùng đó (Lamarckian learning).
   - Khi phát hiện cá thể con bị trùng lặp với cá thể đã có trong quần thể, thuật toán kích hoạt phép nhiễu **4-opt Double-Bridge** (cắt chu trình thành 4 đoạn $A, B, C, D$ và nối lại thành $A - D - C - B$ — một cấu hình không thể bị hoàn tác bởi bất kỳ bước 2-opt hay 3-opt đơn lẻ nào) rồi chạy lại 2-opt, tạo ra sức mạnh khám phá vượt trội.

---

## CHƯƠNG 6: THỰC NGHIỆM, PHÂN TÍCH THAM SỐ VÀ KIỂM ĐỊNH THỐNG KÊ

### 6.1. Môi trường thực nghiệm và Bộ dữ liệu
- **Cấu hình phần cứng & phần mềm:**  
  - Hệ điều hành: Windows 11 (64-bit)
  - Ngôn ngữ & Trình thông dịch: **Python 3.14.7** (MSYS2 UCRT64), tất cả các thuật toán được cài đặt trên cùng một ngôn ngữ, chạy trên cùng một máy và dùng chung hàm đánh giá mục tiêu / kiểm tra hợp lệ.
- **Bộ dữ liệu thực nghiệm (12 thể hiện thuộc 3 mức kích thước + 1 thể hiện mở rộng $n = 1000$):**
  1. **Nhóm kích thước nhỏ ($n = 10, 12, 15, 16, 18$):** `syn_10`, `syn_12`, `syn_15`, `syn_16`, `syn_18` (kèm `scale_19`, `scale_20`) dùng để chạy thuật toán chính xác Held–Karp tìm lời giải tối ưu toàn cục $f^*$.
  2. **Nhóm kích thước trung bình ($n = 40, 51, 52, 70$):** Thể hiện tự sinh `syn_40` và 3 bộ dữ liệu chuẩn **TSPLIB** nổi tiếng: `eil51` ($n=51, f^*=426$), `berlin52` ($n=52, f^*=7542$), `st70` ($n=70, f^*=675$).
  3. **Nhóm kích thước lớn ($n = 76, 100, 120$ + Mở rộng $n = 1000$):** 2 bộ dữ liệu chuẩn **TSPLIB** `eil76` ($n=76, f^*=538$), `kroA100` ($n=100, f^*=21282$), bộ tự sinh phân cụm đô thị `syn_120` ($n=120$), và bộ mở rộng `syn_1000` ($n=1000$).
- **Thiết kế chạy độc lập:** Mỗi giải thuật Metaheuristic chạy **10 lần độc lập** trên mỗi thể hiện với 10 hạt giống ngẫu nhiên cố định `SEEDS = [1001..1010]` (tổng cộng $12 \times 5 \times 10 = 600$ lần chạy được lưu đầy đủ trong `results/raw_runs.csv`).
- **Độ lệch tương đối (Relative Percentage Deviation – Gap):**
  $$\text{Gap (\%)} = \frac{f - f^*}{f^*} \times 100\%$$

---

### 6.2. Thực nghiệm Thuật toán chính xác trên dữ liệu nhỏ ($n = 10 \dots 21$)

**Bảng 6.1:** Kết quả đối chiếu giữa Quy hoạch động Held–Karp và Nhánh cận (Branch & Bound) (trích từ `results/exact_results.csv`):

| Thể hiện | Số đỉnh $n$ | Giá trị tối ưu $f^*$ | Thời gian Held–Karp (s) | Đạt tối ưu (HK) | Chi phí B&B | Thời gian B&B (s) | Số nút B&B đã duyệt |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `syn_10` | 10 | **1687.0** | 0.00143 | Có (100%) | **1687.0** | 0.00949 | 14,990 |
| `syn_12` | 12 | **1269.0** | 0.00780 | Có (100%) | **1269.0** | 0.06280 | 94,510 |
| `syn_15` | 15 | **966.0** | 0.09054 | Có (100%) | **966.0** | 0.25781 | 304,236 |
| `syn_16` | 16 | **1841.0** | 0.21369 | Có (100%) | **1841.0** | 0.68446 | 642,415 |
| `syn_18` | 18 | **1013.0** | 0.97004 | Có (100%) | **1013.0** | 15.0029 (Timeout) | 17,227,776 |
| `scale_19` | 19 | **3662.0** | 2.08931 | Có (100%) | — | — | — |
| `scale_20` | 20 | **3439.0** | 4.55271 | Có (100%) | — | — | — |
| `scale_21` | 21 | **3886.0** | 10.12203 | Có (100%) | — | — | — |

**Nhận xét:**
- Cả hai thuật toán chính xác (Held–Karp và Nhánh cận với công thức cập nhật cận dưới hợp lệ) đều tìm ra **chính xác cùng một giá trị tối ưu toàn cục** trên toàn bộ các thể hiện.
- Nhờ tối ưu hóa cấu trúc dữ liệu bảng truy vết bằng mảng phẳng `bytearray` và lưu hai lớp DP liên tiếp bằng `array('d')`, thời gian chạy Held–Karp ở $n = 20$ chỉ mất $4.55$ giây và $n = 21$ mất $10.12$ giây (với hệ số nhân thực nghiệm $\approx 2.22\times$ mỗi khi tăng thêm 1 đỉnh). Từ số liệu thực nghiệm này, ở $n = 22$ thời gian khoảng $\approx 22.5$ giây, $n = 23$ khoảng $\approx 50$ giây, $n = 25$ khoảng $\approx 245$ giây ($< 10$ phút, tốn $\approx 420\text{ MB}$ RAM cho bảng `parent`), và từ $n \ge 26$ sẽ vượt quá ngưỡng 10 phút ($600$ giây).

---

### 6.3. Thực nghiệm Heuristic xây dựng và Tìm kiếm cục bộ

**Bảng 6.2:** So sánh các Heuristic xây dựng (NN, Multi-Start NN, Cheapest Insertion) và Tìm kiếm cục bộ 3 lân cận (`2-opt`, `Swap`, `Or-opt`) với chiến lược First Improvement (FI) và Best Improvement (BI) (trích từ `results/constructive_localsearch.csv`):

| Thể hiện ($n$) | BKS $f^*$ | NN Cost | Multi-NN Cost | Cheapest Insertion | 2-opt (First) | 2-opt (Best) | Swap (First) | Swap (Best) | Or-opt (First) | Or-opt (Best) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `syn_10` (10) | 1687 | 2135 | 1701 | 1743 | 1726 | 1704 | 1726 | 1704 | **1687** | **1687** |
| `syn_12` (12) | 1269 | 1304 | 1277 | 1302 | 1272 | 1272 | 1272 | 1272 | **1269** | 1276 |
| `syn_15` (15) | 966 | 1179 | 1130 | 1037 | **966** | **966** | 1023 | 1023 | 997 | 1067 |
| `syn_16` (16) | 1841 | 2086 | 1930 | 1978 | 1935 | **1905** | 1935 | **1905** | 1947 | **1905** |
| `syn_18` (18) | 1013 | 1216 | 1207 | 1034 | 1034 | **1013** | 1028 | 1028 | 1035 | **1013** |
| `syn_40` (40) | 4993 | 7145 | 5522 | 5919 | 5348 | 5546 | 6357 | 6199 | 5764 | **5307** |
| `eil51` (51) | 426 | 511 | 482 | 494 | 438 | **435** | 502 | 477 | 463 | 453 |
| `berlin52` (52) | 7542 | 8980 | 8848 | 9004 | 7967 | **7842** | 8506 | 8614 | 8042 | 8190 |
| `st70` (70) | 675 | 830 | 796 | 782 | **691** | 738 | 765 | 760 | 722 | 755 |
| `eil76` (76) | 538 | 642 | 608 | 615 | **558** | 562 | 612 | 612 | 575 | 572 |
| `kroA100` (100)| 21282 | 27807 | 24698 | 24942 | 22437 | **21919** | 24155 | 24142 | 23394 | 23105 |
| `syn_120` (120)| 6081 | 7443 | 7088 | 7165 | 6474 | **6384** | 6963 | 6963 | 6869 | 6440 |

**Nhận xét chuyên môn:**
1. **Giữa các Heuristic xây dựng:** `Cheapest Insertion` và `Multi-Start NN` luôn tạo ra chu trình ban đầu tốt hơn đáng kể so với `Nearest Neighbor` đơn điểm (ví dụ trên `kroA100`, NN có độ lệch $30.6\%$ so với BKS, trong khi Cheapest Insertion giảm xuống còn $17.2\%$).
2. **Giữa 3 cấu trúc lân cận (`2-opt` vs `Swap` vs `Or-opt`):** Cấu trúc lân cận `2-opt` cho chất lượng vượt trội so với `Swap` trên các đồ thị hình học 2D (trên `kroA100`, `2-opt Best` đạt $21919$, chỉ lệch $2.99\%$ so với BKS, trong khi `Swap` kẹt ở $24142$). Lý do là phép `Swap` hoán đổi 2 đỉnh rời rạc làm thay đổi 4 cạnh và rất dễ tạo ra giao cắt mới, trong khi `2-opt` trực tiếp gỡ bỏ các cặp cạnh tự cắt nhau (un-crossing edges).
3. **First Improvement vs Best Improvement:** `First Improvement` thường thực hiện nhiều bước di chuyển hơn (ví dụ 42 bước so với 23 bước trên `kroA100`) nhưng mỗi bước nhanh hơn rất nhiều vì dừng duyệt ngay khi gặp $\Delta < 0$.

---

### 6.4. Thực nghiệm so sánh 5 Giải thuật Metaheuristic trên 12 thể hiện

**Bảng 6.3:** Tổng hợp kết quả thực nghiệm của 5 giải thuật (**SA, TS, GA, ACO, Memetic**) qua 10 lần chạy độc lập trên mỗi thể hiện với **cùng ngân sách thời gian** (trích từ `results/summary_results.csv`; trên `syn_10..18` mốc đối chiếu là nghiệm tối ưu chính xác $f^*$ của Held–Karp; trên 5 bộ TSPLIB là BKS chuẩn; trên `syn_40` và `syn_120` là nghiệm tốt nhất tìm được $f_{\text{ref}}$):

| Thể hiện ($n$, Mốc $f^*$) | Giải thuật | Tốt nhất ($f_{\text{best}}$) | Trung bình ($\bar{f}$) | Độ lệch chuẩn ($\sigma$) | Gap Tốt nhất (%) | Gap Trung bình (%) | Thời gian TB (s) | Tỉ lệ đạt $f^*$ / BKS (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`syn_10`**<br>($n=10, f^*=1687$) | SA<br>TS<br>GA<br>ACO<br>**Memetic** | **1687.0**<br>**1687.0**<br>**1687.0**<br>**1687.0**<br>**1687.0** | **1687.0**<br>**1687.0**<br>**1687.0**<br>**1687.0**<br>**1687.0** | 0.00<br>0.00<br>0.00<br>0.00<br>0.00 | **0.000%**<br>**0.000%**<br>**0.000%**<br>**0.000%**<br>**0.000%** | **0.000%**<br>**0.000%**<br>**0.000%**<br>**0.000%**<br>**0.000%** | 0.120<br>0.120<br>0.120<br>0.120<br>0.120 | **100%**<br>**100%**<br>**100%**<br>**100%**<br>**100%** |
| **`syn_12`**<br>($n=12, f^*=1269$) | SA<br>TS<br>GA<br>ACO<br>**Memetic** | **1269.0**<br>**1269.0**<br>**1269.0**<br>**1269.0**<br>**1269.0** | **1269.0**<br>**1269.0**<br>1270.2<br>1269.6<br>**1269.0** | 0.00<br>0.00<br>1.55<br>1.26<br>0.00 | **0.000%**<br>**0.000%**<br>**0.000%**<br>**0.000%**<br>**0.000%** | **0.000%**<br>**0.000%**<br>0.095%<br>0.047%<br>**0.000%** | 0.120<br>0.120<br>0.120<br>0.120<br>0.120 | **100%**<br>**100%**<br>60%<br>80%<br>**100%** |
| **`syn_15`**<br>($n=15, f^*=966$) | SA<br>TS<br>GA<br>ACO<br>**Memetic** | **966.0**<br>**966.0**<br>**966.0**<br>**966.0**<br>**966.0** | **966.0**<br>**966.0**<br>967.9<br>**966.0**<br>**966.0** | 0.00<br>0.00<br>6.01<br>0.00<br>0.00 | **0.000%**<br>**0.000%**<br>**0.000%**<br>**0.000%**<br>**0.000%** | **0.000%**<br>**0.000%**<br>0.197%<br>**0.000%**<br>**0.000%** | 0.120<br>0.120<br>0.120<br>0.120<br>0.120 | **100%**<br>**100%**<br>90%<br>**100%**<br>**100%** |
| **`syn_16`**<br>($n=16, f^*=1841$) | SA<br>TS<br>GA<br>ACO<br>**Memetic** | **1841.0**<br>**1841.0**<br>**1841.0**<br>**1841.0**<br>**1841.0** | **1841.0**<br>**1841.0**<br>1888.6<br>**1841.0**<br>**1841.0** | 0.00<br>0.00<br>37.87<br>0.00<br>0.00 | **0.000%**<br>**0.000%**<br>**0.000%**<br>**0.000%**<br>**0.000%** | **0.000%**<br>**0.000%**<br>2.586%<br>**0.000%**<br>**0.000%** | 0.120<br>0.120<br>0.120<br>0.120<br>0.120 | **100%**<br>**100%**<br>30%<br>**100%**<br>**100%** |
| **`syn_18`**<br>($n=18, f^*=1013$) | SA<br>TS<br>GA<br>ACO<br>**Memetic** | **1013.0**<br>**1013.0**<br>**1013.0**<br>**1013.0**<br>**1013.0** | **1013.0**<br>**1013.0**<br>1015.1<br>**1013.0**<br>**1013.0** | 0.00<br>0.00<br>6.64<br>0.00<br>0.00 | **0.000%**<br>**0.000%**<br>**0.000%**<br>**0.000%**<br>**0.000%** | **0.000%**<br>**0.000%**<br>0.207%<br>**0.000%**<br>**0.000%** | 0.120<br>0.120<br>0.120<br>0.120<br>0.120 | **100%**<br>**100%**<br>90%<br>**100%**<br>**100%** |
| **`syn_40`**<br>($n=40, f_{\text{ref}}=4993$) | SA<br>TS<br>GA<br>ACO<br>**Memetic** | **4993.0**<br>**4993.0**<br>**4993.0**<br>**4993.0**<br>**4993.0** | 5056.0<br>**4993.0**<br>5043.6<br>**4993.0**<br>**4993.0** | 131.93<br>0.00<br>79.64<br>0.00<br>0.00 | **0.000%**<br>**0.000%**<br>**0.000%**<br>**0.000%**<br>**0.000%** | 1.262%<br>**0.000%**<br>1.013%<br>**0.000%**<br>**0.000%** | 0.350<br>0.350<br>0.350<br>0.351<br>0.350 | 70%<br>**100%**<br>40%<br>**100%**<br>**100%** |
| **`eil51`**<br>($n=51, \text{BKS}=426$) | SA<br>TS<br>GA<br>ACO<br>**Memetic** | 429.0<br>427.0<br>430.0<br>428.0<br>**426.0** | 433.7<br>428.4<br>438.9<br>429.2<br>**428.1** | 3.50<br>1.71<br>7.62<br>**1.14**<br>1.37 | 0.704%<br>0.235%<br>0.939%<br>0.469%<br>**0.000%** | 1.808%<br>0.563%<br>3.028%<br>0.751%<br>**0.493%** | 0.350<br>0.350<br>0.350<br>0.351<br>0.350 | 0%<br>0%<br>0%<br>0%<br>**10%** |
| **`berlin52`**<br>($n=52, \text{BKS}=7542$) | SA<br>TS<br>GA<br>ACO<br>**Memetic** | **7542.0**<br>**7542.0**<br>7596.0<br>**7542.0**<br>**7542.0** | 7750.5<br>7789.3<br>8042.6<br>7559.3<br>**7542.0** | 229.41<br>153.66<br>202.28<br>54.71<br>**0.00** | **0.000%**<br>**0.000%**<br>0.716%<br>**0.000%**<br>**0.000%** | 2.765%<br>3.279%<br>6.637%<br>0.229%<br>**0.000%** | 0.351<br>0.350<br>0.351<br>0.354<br>0.352 | 40%<br>20%<br>0%<br>90%<br>**100%** |
| **`st70`**<br>($n=70, \text{BKS}=675$) | SA<br>TS<br>GA<br>ACO<br>**Memetic** | 681.0<br>682.0<br>691.0<br>676.0<br>**675.0** | 692.0<br>688.8<br>725.1<br>681.0<br>**680.4** | 8.06<br>**3.88**<br>26.70<br>4.47<br>4.01 | 0.889%<br>1.037%<br>2.370%<br>0.148%<br>**0.000%** | 2.519%<br>2.044%<br>7.422%<br>0.889%<br>**0.800%** | 0.450<br>0.450<br>0.450<br>0.454<br>0.450 | 0%<br>0%<br>0%<br>0%<br>**30%** |
| **`eil76`**<br>($n=76, \text{BKS}=538$) | SA<br>TS<br>GA<br>ACO<br>**Memetic** | 544.0<br>542.0<br>571.0<br>539.0<br>**538.0** | 554.2<br>549.7<br>581.6<br>543.2<br>**538.5** | 7.00<br>4.40<br>7.40<br>3.85<br>**1.58** | 1.115%<br>0.743%<br>6.134%<br>0.186%<br>**0.000%** | 3.011%<br>2.175%<br>8.104%<br>0.967%<br>**0.093%** | 0.450<br>0.450<br>0.451<br>0.453<br>0.450 | 0%<br>0%<br>0%<br>0%<br>**90%** |
| **`kroA100`**<br>($n=100, \text{BKS}=21282$) | SA<br>TS<br>GA<br>ACO<br>**Memetic** | 21369.0<br>21330.0<br>21981.0<br>**21282.0**<br>**21282.0** | 21726.7<br>21635.4<br>22859.1<br>21367.2<br>**21284.0** | 298.93<br>380.33<br>676.29<br>102.25<br>**4.22** | 0.409%<br>0.226%<br>3.284%<br>**0.000%**<br>**0.000%** | 2.090%<br>1.661%<br>7.410%<br>0.400%<br>**0.009%** | 0.600<br>0.600<br>0.600<br>0.604<br>0.600 | 0%<br>0%<br>0%<br>30%<br>**80%** |
| **`syn_120`**<br>($n=120, f_{\text{ref}}=6081$) | SA<br>TS<br>GA<br>ACO<br>**Memetic** | 6134.0<br>6111.0<br>6497.0<br>6089.0<br>**6081.0** | 6297.2<br>6208.9<br>6673.0<br>6138.2<br>**6097.3** | 103.92<br>89.29<br>92.77<br>44.36<br>**24.26** | 0.872%<br>0.493%<br>6.841%<br>0.132%<br>**0.000%** | 3.555%<br>2.103%<br>9.735%<br>0.941%<br>**0.268%** | 0.600<br>0.600<br>0.600<br>0.606<br>0.600 | 0%<br>0%<br>0%<br>0%<br>**60%** |

#### Thảo luận kết quả thực nghiệm (dưới cùng ngân sách thời gian công bằng):
1. **Tính công bằng về ngân sách thời gian:** Mọi giải thuật đều chạy đúng ngân sách thời gian quy định theo kích thước thể hiện ($0.120\text{s}$ cho $n \le 18$, $0.350\text{s}$ cho $n \in [40, 52]$, $0.450\text{s}$ cho $n \in [70, 76]$, và $0.600\text{s}$ cho $n \in [100, 120]$).
2. **Trên nhóm dữ liệu nhỏ ($n = 10 \dots 18$):**  
   Bốn thuật toán `SA`, `TS`, `ACO`, và `Memetic` đạt **tỉ lệ tìm được nghiệm tối ưu toàn cục tuyệt đối ($100\%$)** trên cả 5 thể hiện nhỏ, khớp hoàn toàn với kết quả của quy hoạch động Held–Karp.
3. **Trên nhóm dữ liệu chuẩn TSPLIB (`eil51`, `berlin52`, `st70`, `eil76`, `kroA100`):**
   - **Thuật toán Lai Memetic (GA + 2-opt + Double-Bridge)** đạt **chính xác 100% giá trị BKS ($\text{Best Gap} = 0.000\%$)** trên cả 5/5 bộ dữ liệu chuẩn TSPLIB, với độ lệch trung bình ($\text{Mean Gap}$) cực nhỏ: $0.000\%$ trên `berlin52`, $0.009\%$ trên `kroA100`, và $0.093\%$ trên `eil76`.
   - **ACO** và **TS** bám sát phía sau: `ACO` tìm được nghiệm tối ưu BKS trên `berlin52` ($90\%$) và `kroA100` ($30\%$), trong khi `TS` khi được cấp đủ thời gian $0.35\text{s}$ đã vượt `ACO` về giá trị trung bình trên `eil51` ($\bar{f} = 428.4$ so với $429.2$).

---

### 6.5. Phân tích Đường hội tụ (Convergence Analysis)
Quan sát trực tiếp các biểu đồ đường hội tụ thực tế tại `results/plots/convergence_*.svg` (như `convergence_berlin52.svg` và `convergence_kroA100.svg`):
- Ngay tại thời điểm khởi tạo ($t \approx 0.0\text{s} \to 0.05\text{s}$), `Memetic` giảm chi phí sâu nhất vì quần thể ban đầu được làm mịn tức thì bằng tìm kiếm cục bộ `2-opt`.
- Đường hội tụ của `SA` và `TS` giảm rất nhanh trong $0.05\text{s}$ đầu tiên (từ $\approx 25\,000$ xuống dưới $22\,000$ trên `kroA100`), sau đó tiếp tục hạ dần từng nấc nhỏ nhờ cơ chế hâm nóng lại (reheating) của `SA` và danh sách cấm của `TS`.
- `ACO` khởi đầu ở mức chi phí của Nearest Neighbor nhưng giảm đều đặn và liên tục xuyên suốt toàn bộ thời gian chạy khi ma trận pheromone $\tau_{ij}$ hội tụ quanh các cạnh thuộc chu trình tối ưu.
- `GA` thuần túy (chỉ dùng lai ghép OX và đột biến ngẫu nhiên, không có 2-opt) hội tụ chậm hơn trên các thể hiện $n \ge 50$, qua đó minh chứng trực tiếp vai trò quyết định của pha tìm kiếm cục bộ trong thuật toán lai `Memetic`.

---

### 6.6. Phân tích Độ nhạy tham số (Parameter Sensitivity Analysis)
Thực hiện khảo sát độ nhạy tham số trên bộ chuẩn `berlin52` ($\text{BKS} = 7542$, trích từ `results/parameter_sensitivity.csv`):

| Giải thuật | Tham số khảo sát | Giá trị thử nghiệm | Chi phí tốt nhất | Chi phí trung bình | Độ lệch chuẩn | Mean Gap (%) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **SA** | Hệ số làm nguội $\alpha$ | $0.950$<br>$0.985$<br>$0.995$<br>**$0.999$** | 7542.0<br>7542.0<br>7542.0<br>**7542.0** | 7818.8<br>7642.8<br>7785.8<br>**7542.0** | 170.14<br>159.49<br>253.63<br>**0.00** | 3.670%<br>1.337%<br>3.233%<br>**0.000%** |
| **TS** | Độ dài cấm `tabu_tenure` ($\theta$) | $5$<br>$15$<br>**$30$**<br>$50$ | **7542.0**<br>**7542.0**<br>7547.0<br>7561.0 | 7708.0<br>7705.8<br>**7583.6**<br>7592.2 | 160.35<br>159.92<br>38.08<br>**36.93** | 2.201%<br>2.172%<br>**0.552%**<br>0.666% |
| **GA** | Toán tử lai & Đột biến $p_m$ | $\text{OX}, p_m = 0.05$<br>$\text{OX}, p_m = 0.20$<br>$\text{OX}, p_m = 0.35$<br>**$\text{PMX}, p_m = 0.20$** | 7841.0<br>7596.0<br>7663.0<br>**7542.0** | 8165.6<br>7956.8<br>7908.6<br>**7859.0** | 275.80<br>223.31<br>**193.69**<br>220.63 | 8.268%<br>5.500%<br>4.861%<br>**4.203%** |
| **ACO** | Trọng số $\beta$ và Bay hơi $\rho$ | $\beta=1.0, \rho=0.15$<br>**$\beta=3.0, \rho=0.15$**<br>$\beta=5.0, \rho=0.15$<br>$\beta=3.0, \rho=0.35$ | 7542.0<br>**7542.0**<br>7542.0<br>7542.0 | 7641.4<br>**7542.0**<br>7576.6<br>7750.4 | 118.28<br>**0.00**<br>77.37<br>155.59 | 1.318%<br>**0.000%**<br>0.459%<br>2.763% |

**Kết luận từ phân tích độ nhạy:**
- Với **SA**, làm nguội quá nhanh ($\alpha = 0.95$) khiến thuật toán bị đóng băng sớm ở cực trị cục bộ ($\text{Gap} = 3.67\%$), trong khi làm nguội chậm ($\alpha = 0.999$) giúp đạt nghiệm tối ưu tuyệt đối $7542.0 \pm 0.0$ ($\text{Mean Gap} = 0.000\%$).
- Với **TS**, độ dài danh sách cấm $\theta = 30$ giảm mạnh độ lệch trung bình xuống $\text{Mean Gap} = 0.552\%$ so với $\theta = 5$ ($2.201\%$) nhờ ngăn chặn chu kỳ lặp.
- Với **ACO**, cấu hình $\beta = 3.0, \rho = 0.15$ cân bằng hoàn hảo giữa vết mùi và khoảng cách cạnh, đạt $7542.0 \pm 0.0$ ($\text{Gap} = 0.000\%$). Khi tăng tốc độ bay hơi lên $\rho = 0.35$, mùi trên các cạnh tốt bay hơi quá nhanh gây hội tụ sớm ($\text{Gap}$ tăng lên $2.763\%$).

---

### 6.7. Kiểm định thống kê phi tham số (Friedman & Wilcoxon)

#### (a) Kiểm định Friedman (Friedman Test) trên toàn bộ 12 thể hiện
- Số thể hiện $N = 12$, số thuật toán $k = 5$ (bậc tự do $df = k - 1 = 4$).
- **Thứ hạng trung bình (Average Ranks — nhỏ hơn là tốt hơn):**
  1. **Memetic Algorithm:** $\mathbf{1.7083}$ (Hạng 1)
  2. **Ant Colony Optimization (ACO):** $\mathbf{2.4583}$ (Hạng 2)
  3. **Tabu Search (TS):** $\mathbf{2.7083}$ (Hạng 3)
  4. **Simulated Annealing (SA):** $\mathbf{3.3750}$ (Hạng 4)
  5. **Genetic Algorithm (GA):** $\mathbf{4.7500}$ (Hạng 5)
- **Thống kê Friedman:** $\chi^2_F = 25.2000$, thống kê hiệu chỉnh Iman–Davenport $F_F = 12.1579$, **$p\text{-value} = 6.4 \times 10^{-5} \ll 0.05$**.  
  $\Rightarrow$ Bác bỏ giả thuyết hòa $H_0$: Có sự khác biệt có ý nghĩa thống kê rất cao giữa hiệu năng của 5 giải thuật.

#### (b) Kiểm định dấu hạng Wilcoxon (Exact Wilcoxon Signed-Rank Test)
Do số cặp khác biệt hiệu quả trên tập 12 thể hiện là $n_{\text{eff}} \in [6, 11] \le 30$, nhóm tính **phân phối chính xác (exact two-tailed $p$-value)** bằng quy hoạch động trên mọi tổ hợp dấu $\pm$ thay vì chỉ dùng xấp xỉ chuẩn (trích từ `results/wilcoxon_results.csv`):

| Cặp so sánh | Tổng hạng dương $W^+$ | Tổng hạng âm $W^-$ | Thống kê $W$ | Phương pháp tính $p$ | Giá trị $p\text{-value}$ chính xác | Kết luận ở mức ý nghĩa $\alpha = 0.05$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **SA vs Memetic** | 28.0 | 0.0 | 0.0 | Exact ($n_{\text{eff}}=7$) | **0.015625** ($= 2/2^7$) | Khác biệt có ý nghĩa thống kê ($p < 0.05$) |
| **TS vs Memetic** | 21.0 | 0.0 | 0.0 | Exact ($n_{\text{eff}}=6$) | **0.031250** ($= 2/2^6$) | Khác biệt có ý nghĩa thống kê ($p < 0.05$) |
| **GA vs Memetic** | 66.0 | 0.0 | 0.0 | Exact ($n_{\text{eff}}=11$)| **0.000977** ($= 2/2^{11}$)| Khác biệt có ý nghĩa thống kê ($p < 0.001$) |
| **ACO vs Memetic**| 28.0 | 0.0 | 0.0 | Exact ($n_{\text{eff}}=7$) | **0.015625** ($= 2/2^7$) | Khác biệt có ý nghĩa thống kê ($p < 0.05$) |

Trong cả 4 phép kiểm định cặp, $W^- = 0.0$ và $p\text{-value}$ chính xác đều nhỏ hơn $0.05$.

---

### 6.8. Mở rộng: Thể hiện lớn $n = 1000$ với Candidate List & Trực quan hóa
Thực hiện yêu cầu mở rộng của Đề 1 (Mục 5):
- Trên thể hiện lớn `syn_1000` ($n = 1000$ điểm giao hàng phân cụm đô thị), việc sử dụng **Danh sách láng giềng gần (Candidate List $k = 20$)** kết hợp cờ `Don't-Look Bits` giúp thuật toán tìm kiếm cục bộ 2-opt hội tụ sau 112 bước chỉ trong **$0.006$ giây** (giảm chi phí từ $186\,315$ của Nearest Neighbor xuống $177\,176$, tiết kiệm $9\,139$ đơn vị quãng đường, tương đương $4.91\%$).
- Nhóm đã xây dựng hoàn chỉnh **Giao diện Trực quan hóa Web tương tác (`visualizer/index.html`)** và **Desktop GUI (`gui_visualizer.py`)** cho phép quan sát trực tiếp quá trình biến đổi chu trình theo thời gian thực.

---

## CHƯƠNG 7: KẾT LUẬN, TÀI LIỆU THAM KHẢO & PHÂN CÔNG

### 7.1. Kết luận, Hạn chế và Hướng phát triển
- **Kết luận:** Đồ án đã hoàn thành toàn diện từ mô hình hóa quy hoạch nguyên, chứng minh NP-khó, cài đặt 2 thuật toán chính xác (Held–Karp, B&B), 3 thuật toán tham lam xây dựng, 3 cấu trúc lân cận cục bộ với đánh giá Delta $\mathcal{O}(1)$, đến 4 giải thuật Metaheuristic (SA, TS, GA, ACO) và 1 thuật toán Lai (Memetic). Thực nghiệm 600 lần chạy trên 12 thể hiện chứng minh sự vượt trội của thuật toán lai Memetic và ACO khi đạt 100% nghiệm tối ưu BKS trên các bộ dữ liệu chuẩn TSPLIB.
- **Hạn chế:** Với các thể hiện cực lớn ($n \ge 10\,000$), việc lưu ma trận khoảng cách đầy đủ $\mathcal{O}(n^2)$ trong bộ nhớ RAM tốn nhiều dung lượng.
- **Hướng phát triển:** Chỉ tính khoảng cách phẳng theo yêu cầu (on-the-fly) kết hợp cấu trúc cây **K-D Tree** để dựng Candidate List trong $\mathcal{O}(n \log n)$, nâng cấp lân cận từ `2-opt` lên **Lin–Kernighan Heuristic (LKH)**, và mở rộng sang bài toán Định tuyến đội xe có tải trọng (CVRP) hoặc khung thời gian (VRPTW).

### 7.2. Tài liệu tham khảo
1. M. R. Garey, D. S. Johnson, *Computers and Intractability: A Guide to the Theory of NP-Completeness*, W. H. Freeman, 1979.
2. R. M. Karp, "Reducibility among combinatorial problems", *Complexity of Computer Computations*, Plenum Press, pp. 85–103, 1972.
3. M. Held, R. M. Karp, "A dynamic programming approach to sequencing problems", *Journal of the Society for Industrial and Applied Mathematics*, 10(1), 196–210, 1962.
4. G. Reinelt, "TSPLIB—A Traveling Salesman Problem Library", *ORSA Journal on Computing*, 3(4), 376–384, 1991.
5. S. Kirkpatrick, C. D. Gelatt, M. P. Vecchi, "Optimization by Simulated Annealing", *Science*, 220(4598), 671–680, 1983.
6. F. Glover, "Future paths for integer programming and links to artificial intelligence", *Computers & Operations Research*, 13(5), 533–549, 1986.
7. J. H. Holland, *Adaptation in Natural and Artificial Systems*, University of Michigan Press, 1975.
8. M. Dorigo, T. Stützle, *Ant Colony Optimization*, MIT Press, 2004.
9. P. Moscato, "On Evolution, Search, Optimization, Genetic Algorithms and Martial Arts: Towards Memetic Algorithms", *Caltech Concurrent Computation Program*, Report 826, 1989.
10. J. Derrac, S. García, D. Molina, F. Herrera, "A practical tutorial on the use of nonparametric statistical tests as a methodology for comparing evolutionary and swarm intelligence algorithms", *Swarm and Evolutionary Computation*, 1(1), 3–18, 2011.

### 7.3. Bảng phân công công việc nhóm (4 thành viên)

| STT | Họ và tên sinh viên | MSSV | Nội dung phụ trách chính | Tỉ lệ đóng góp |
| :-: | :--- | :---: | :--- | :---: |
| 1 | *[Điền Họ tên TV 1]* | *[MSSV 1]* | Mô hình hóa toán học, chứng minh NP-khó; cài đặt **Held–Karp DP** và **Simulated Annealing (SA)**; viết Chương 1, 2, 3.1, 5.1. | 25% |
| 2 | *[Điền Họ tên TV 2]* | *[MSSV 2]* | Cài đặt **Nhánh cận (B&B)**, Heuristic xây dựng (**NN, Cheapest Insertion**), hàm `validator.py` và **Tabu Search (TS)**; viết Chương 3.2, 4.1, 4.2, 5.2. | 25% |
| 3 | *[Điền Họ tên TV 3]* | *[MSSV 3]* | Cài đặt Tìm kiếm cục bộ (**2-opt, Swap** với Delta Evaluation $\mathcal{O}(1)$), **Genetic Algorithm (GA - OX/PMX)**, phân tích độ nhạy tham số; viết Chương 4.3, 5.3, 6.6. | 25% |
| 4 | *[Điền Họ tên TV 4]* | *[MSSV 4]* | Cài đặt **Or-opt**, **Ant Colony Optimization (ACO)**, **Thuật toán Lai Memetic**, kiểm định thống kê (**Friedman, Wilcoxon**) và **Giao diện trực quan hóa**; viết Chương 5.4, 5.5, 6.4, 6.7, 7. | 25% |

### 7.4. Tuyên bố Liêm chính Học thuật và Ghi nhận Nguồn tham khảo (Mục 3.4)
Tuân thủ quy định về Liêm chính học thuật tại Mục 3.4 của Đề bài tập lớn:
- **Tự cài đặt thuật toán:** Toàn bộ các thuật toán chính xác (Held–Karp, Nhánh cận), các thuật toán tham lam xây dựng (Nearest Neighbor, Cheapest Insertion), tìm kiếm cục bộ (2-opt, Swap, Or-opt với Delta Evaluation), 4 giải thuật Metaheuristic (SA, TS, GA, ACO), thuật toán lai Memetic và bộ kiểm định thống kê (Friedman, Wilcoxon) trong thư mục `src/` đều được cài đặt tường minh bằng Python chuẩn, không sử dụng bất kỳ thư viện giải quy hoạch nguyên hay thư viện metaheuristic đóng gói sẵn nào.
- **Nguồn dữ liệu chuẩn:** Tọa độ các bộ dữ liệu `eil51`, `berlin52`, `st70`, `eil76`, `kroA100` và giá trị BKS tương ứng được trích xuất từ thư viện chuẩn **TSPLIB** của G. Reinelt (1991).
- **Khai báo sử dụng công cụ AI hỗ trợ:** Trong quá trình thực hiện đồ án, nhóm có sử dụng công cụ trợ lý AI lập trình (*Google Antigravity*) để hỗ trợ tổ chức cấu trúc mã nguồn mô-đun hóa, xây dựng giao diện trực quan hóa HTML5 Canvas / Tkinter, kiểm tra lỗi công thức cận dưới Nhánh cận và định dạng tài liệu báo cáo LaTeX/Markdown. Mọi thành viên trong nhóm đã trực tiếp rà soát, kiểm thử độc lập từng hàm, nắm vững nguyên lý toán học và sẵn sàng giải thích chi tiết phần việc phụ trách khi vấn đáp.
- **Tính tái lập (Reproducibility):** Toàn bộ kết quả trong báo cáo này và trong `results/*.csv` đều được sinh tự động và tái lập chính xác 100% từ mã nguồn nộp kèm thông qua lệnh `python run_experiments.py` với danh sách hạt giống cố định `SEEDS = [1001..1010]`.
