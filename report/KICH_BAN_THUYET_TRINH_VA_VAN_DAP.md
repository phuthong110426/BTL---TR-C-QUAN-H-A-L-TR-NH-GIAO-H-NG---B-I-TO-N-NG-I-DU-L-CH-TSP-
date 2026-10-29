# KỊCH BẢN THUYẾT TRÌNH TỪNG SLIDE & CẨM NANG TRẢ LỜI VẤN ĐÁP (3.0 ĐIỂM)
**Đề tài 1: Lộ trình xe giao hàng — Bài toán Người du lịch (TSP)**

> **Lưu ý quan trọng từ Đề bài (Mục 4.1 & 6.2):**  
> Phần thuyết trình & vấn đáp chiếm **3.0 / 10 điểm**. Giảng viên sẽ hỏi ngẫu nhiên từng thành viên về: (1) Hiểu nguyên lý thuật toán, (2) Chỉ ra đúng dòng code trong dự án, và (3) Giải thích tại sao thuật toán này chạy tốt hơn thuật toán kia. Tài liệu này giúp cả 4 thành viên hiểu bản chất từ gốc và nắm sẵn lời thoại tự nhiên nhất.

---

## PHẦN 1: LỜI THOẠI THUYẾT TRÌNH TỪNG SLIDE (15–20 PHÚT CHO 4 THÀNH VIÊN)

### 👤 THÀNH VIÊN 1: Trình bày Slide 1, 2, 3, 4 (Khoảng 4–5 phút)

#### **Slide 1 & Slide 2: Phát biểu bài toán & Mô hình toán học ILP**
- **Bản chất dễ hiểu:** Hãy tưởng tượng một shipper Shopee xuất phát từ kho (đỉnh $0$), cần giao hàng cho $n-1$ khách hàng rồi quay về kho. Đi thứ tự nào để tốn ít xăng nhất? Đó chính là bài toán TSP.
- **Lời thoại nói trước lớp:**
  > *"Chào thầy/cô và các bạn. Nhóm em gồm 4 thành viên, thực hiện Đề tài 1: Bài toán Người du lịch (TSP) ứng dụng cho lộ trình xe giao hàng.  
  > Về mặt toán học (Slide 2), nhóm mô hình hóa bài toán dưới dạng Quy hoạch nguyên tuyến tính (ILP) với biến quyết định $x_{ij} = 1$ nếu xe đi trực tiếp từ điểm $i$ sang điểm $j$. Hai ràng buộc đầu đảm bảo mỗi điểm chỉ được đến 1 lần và rời đi 1 lần. Điểm quan trọng nhất là **ràng buộc thứ ba (DFJ)**: nó ngăn không cho lời giải bị tách thành các vòng tròn nhỏ rời rạc (gọi là chu trình con - subtour).  
  > Trong code, nhóm biểu diễn mỗi lộ trình là một mảng hoán vị từ $0$ đến $n-1$, và viết hàm kiểm tra độc lập `validate_tour` trong tệp `src/validator.py` để đảm bảo 100% lời giải không bị lặp đỉnh hay tính sai chi phí."*

#### **Slide 3: Tại sao bài toán này là NP-khó? (Sự bùng nổ tổ hợp)**
- **Bản chất dễ hiểu:** Tại sao không cho máy tính thử hết mọi cách đi? Vì số cách đi là $\frac{(n-1)!}{2}$, tăng nhanh khủng khiếp. Với 52 điểm (`berlin52`), số cách đi là $7.75 \times 10^{65}$ — siêu máy tính chạy mất hàng chục tỷ tỷ năm.
- **Lời thoại nói trước lớp:**
  > *"Ở Slide 3, nhóm chứng minh phiên bản quyết định `TSP-DECISION` là NP-đầy đủ bằng phép quy dẫn từ bài toán Chu trình Hamilton (theo Karp, 1972): ta gán cạnh có thật bằng 1, cạnh không có thật bằng 2 và hỏi có chu trình nào tổng độ dài $\le n$ hay không.  
  > Bảng bên phải cho thấy sự bùng nổ tổ hợp: với $n=10$ chỉ có 181 nghìn chu trình, nhưng đến $n=52$ của bộ dữ liệu chuẩn `berlin52` đã lên tới $10^{65}$ chu trình. Vì vậy, không thể duyệt vét cạn mà phải dùng Quy hoạch động cho cỡ nhỏ và Metaheuristic cho cỡ lớn."*

#### **Slide 4: Thuật toán chính xác (Held–Karp DP & Nhánh cận)**
- **Bản chất dễ hiểu:**
  - **Held–Karp (`solve_held_karp`):** Thay vì thử từng thứ tự ($n!$), ta dùng dãy nhị phân (bitmask) $S$ để đánh dấu *"những điểm nào đã đi qua"* và $u$ là *"điểm đang đứng hiện tại"*. Số trạng thái giảm từ $n!$ xuống $n \cdot 2^n$.
  - **Nhánh cận (`solve_branch_and_bound`):** Đi thử từng nhánh trên cây tìm kiếm. Ở mỗi nhánh, ta ước lượng *"dù đi tiếp tối ưu nhất thì chi phí tối thiểu (cận dưới $LB$) cũng là bao nhiêu"*. Nếu $LB \ge$ kỷ lục hiện tại ($UB$) thì cắt bỏ luôn nhánh đó không đi tiếp nữa.
- **Lời thoại nói trước lớp:**
  > *"Ở Chương 3 (Slide 4), nhóm tự cài đặt 2 thuật toán chính xác trong `src/exact_solver.py`.  
  > Thứ nhất là Quy hoạch động bitmask Held–Karp độ phức tạp $\mathcal{O}(n^2 2^n)$. Để không bị tràn RAM trên Python, nhóm dùng mảng phẳng 1 chiều `bytearray` lưu vết và giải chính xác tới $n=21$ đỉnh trong 10 giây.  
  > Thứ hai là Nhánh cận (Branch and Bound) sử dụng cận dưới bằng nửa tổng 2 cạnh ngắn nhất nối với mỗi đỉnh. Cả hai thuật toán cho kết quả khớp nhau tuyệt đối 100% trên mọi bộ dữ liệu nhỏ từ 10 đến 18 đỉnh."*

---

### 👤 THÀNH VIÊN 2: Trình bày Slide 5 (Khoảng 3–4 phút)

#### **Slide 5: Heuristic xây dựng & Tìm kiếm cục bộ (Delta Evaluation $\mathcal{O}(1)$)**
- **Bản chất dễ hiểu:**
  - **Heuristic tham lam (`Nearest Neighbor`):** Đứng ở đâu thì cứ chọn điểm gần nhất chưa đi mà bước tới. Chạy cực nhanh nhưng bước cuối cùng hay phải nối về kho bằng một đường rất xa (sai số khoảng 15%–25%).
  - **Tìm kiếm cục bộ (`Local Search`):** Lấy lộ trình tham lam đó đem sửa dần. Nhóm cài 3 cách sửa (3 cấu trúc lân cận):
    1. **`2-opt` (Đảo đoạn):** Khi 2 đường đi bị bắt chéo nhau thành hình chữ X, ta cắt 2 cạnh chéo đó ra và nối song song lại (tương đương lật ngược đoạn ở giữa).
    2. **`Swap`:** Đổi chỗ 2 điểm bất kỳ trong lộ trình.
    3. **`Or-opt`:** Bốc một cụm 1, 2 hoặc 3 điểm liên tiếp đem chèn sang chỗ khác.
  - **Delta Evaluation $\mathcal{O}(1)$ là gì? (Câu hỏi thầy cô cực hay hỏi!):** Khi đảo đoạn `2-opt`, 98% các cạnh trong lộ trình giữ nguyên, chỉ có **2 cạnh cũ bị xóa** và **2 cạnh mới được thêm vào**. Thay vì dùng vòng lặp `for` cộng lại cả $n$ cạnh tốn $\mathcal{O}(n)$, ta chỉ lấy `(2 cạnh mới) - (2 cạnh cũ)` tốn đúng 4 phép tính ($\mathcal{O}(1)$). Nhờ vậy thuật toán chạy nhanh gấp hàng trăm lần!
- **Lời thoại nói trước lớp:**
  > *"Em xin trình bày Chương 4 (Slide 5) về Heuristic xây dựng và Tìm kiếm cục bộ trong `src/constructive.py` và `src/local_search.py`.  
  > Sau khi tạo lộ trình ban đầu bằng Láng giềng gần nhất (NN) hoặc Chèn rẻ nhất (CI), nhóm cải thiện lộ trình bằng 3 cấu trúc lân cận: `2-opt`, `Swap` và `Or-opt`, với cả hai chiến lược First Improvement (thấy tốt hơn là nhận ngay) và Best Improvement (xét hết rồi chọn bước giảm sâu nhất).  
  > Điểm kỹ thuật cốt lõi ở đây là **Delta Evaluation $\mathcal{O}(1)$**: mỗi phép thử chỉ tính hiệu số giữa các cạnh thêm vào và cạnh mất đi trong thời gian hằng số. Bảng kết quả bên phải cho thấy `2-opt` hiệu quả vượt trội nhất vì nó gỡ trực tiếp các cạnh giao cắt hình học, kéo sai số từ hơn 20% xuống chỉ còn khoảng 3% trong chưa đầy 2 mili-giây."*

---

### 👤 THÀNH VIÊN 3: Trình bày nửa đầu Slide 6 & Slide 7 (Khoảng 4 phút)

#### **Slide 6 (Phần SA, TS, GA): Các giải thuật Metaheuristic**
- **Bản chất dễ hiểu:** Tại sao có `2-opt` rồi vẫn cần Metaheuristic? Vì `2-opt` chỉ đi xuống dốc — hễ rơi vào một cái hố nhỏ (cực trị địa phương - local optimum) là nó đứng im luôn. Metaheuristic giúp **nhảy thoát khỏi cái hố đó** để tìm hố sâu hơn:
  1. **Simulated Annealing (SA - Tôi luyện kim loại):** Cho phép nhận cả bước đi **xấu hơn** ($\Delta > 0$) với xác suất $e^{-\Delta / T}$. Lúc đầu nhiệt độ $T$ cao thì hay nhảy lung tung để khám phá; sau đó $T$ giảm dần ($T \leftarrow 0.995 T$) để hội tụ.
  2. **Tabu Search (TS - Tìm kiếm cấm):** Bắt buộc phải đi tiếp kể cả khi mọi bước xung quanh đều xấu hơn, nhưng để không bị quay lại chỗ cũ (lặp vô tận), nó ghi các cạnh vừa cắt vào **Danh sách cấm (Tabu List)** trong $\theta$ bước. Nếu một bước bị cấm nhưng lại phá kỷ lục tốt nhất từ trước tới nay thì vẫn cho đi (**Aspiration Criterion**).
  3. **Genetic Algorithm (GA - Giải thuật Di truyền):** Duy trì một quần thể 60 lộ trình. Cho các lộ trình tốt "lai ghép" với nhau bằng phép lai **Order Crossover (OX)** và **PMX** (copy một đoạn của Cha, phần còn lại lấy theo thứ tự của Mẹ để không bị trùng thành phố nào).
- **Lời thoại nói trước lớp:**
  > *"Để thoát khỏi cực trị địa phương của Local Search, ở Chương 5 (Slide 6), nhóm cài đặt 4 giải thuật Metaheuristic trong `src/metaheuristics.py`.  
  > Với nhóm đơn lời giải: **Simulated Annealing (SA)** thoát bẫy bằng cách chấp nhận bước đi xấu theo xác suất Boltzmann $e^{-\Delta/T}$ kèm cơ chế hâm nóng lại (reheating); còn **Tabu Search (TS)** sử dụng bộ nhớ ngắn hạn cấm cắt lại các cạnh vừa thay đổi trong $\lfloor 2.5\sqrt{n}\rfloor$ vòng lặp, kết hợp tiêu chí mong đợi Aspiration Criterion.  
  > Với nhóm quần thể: **Genetic Algorithm (GA)** sử dụng mã hóa hoán vị và hai toán tử lai ghép chuyên biệt cho TSP là **OX** và **PMX**, đảm bảo 100% cá thể con sinh ra là chu trình hợp lệ mà không bị trùng đỉnh."*

---

### 👤 THÀNH VIÊN 4: Trình bày phần ACO, Memetic (Slide 6), Slide 7, Slide 8 & Demo (Khoảng 4–5 phút)

#### **Slide 6 (ACO & Memetic) + Slide 7 & 8: Thuật toán Đàn kiến, Memetic, Thống kê & Demo**
- **Bản chất dễ hiểu:**
  - **Ant Colony Optimization (ACO / MMAS):** Mô phỏng đàn kiến tìm đường. Kiến chọn cạnh dựa trên 2 yếu tố: **vết mùi pheromone ($\tau_{ij}$)** của kiến đi trước để lại và **khoảng cách gần ($\eta_{ij} = 1/d_{ij}$)**. Sau mỗi vòng, cạnh thuộc lộ trình tốt nhất được bồi đắp thêm mùi.
  - **Thuật toán Lai Memetic (Mạnh nhất đồ án):** GA truyền thống lai ghép xong thì cá thể con thường bị rối cạnh. Memetic khắc phục bằng cách: **Lai ghép OX xong $\rightarrow$ chạy ngay `2-opt` trên từng đứa con** để làm phẳng lộ trình, kết hợp cú đá **4-opt Double-Bridge** khi bị kẹt.
  - **Kiểm định thống kê Friedman & Wilcoxon:** Chạy 600 lần (12 bộ dữ liệu $\times$ 5 thuật toán $\times$ 10 seeds) với **cùng ngân sách thời gian**. Trị số $p\text{-value} < 0.05$ chứng minh toán học rằng Memetic thắng các thuật toán khác là do bản chất thuật toán thực sự tốt hơn chứ không phải do ăn may ngẫu nhiên.
- **Lời thoại nói trước lớp:**
  > *"Tiếp nối phần quần thể, em trình bày **Ant Colony Optimization (ACO)** theo biến thể Max-Min Ant System: đàn kiến xây dựng chu trình trên danh sách 20 láng giềng gần nhất và giới hạn ngưỡng mùi $[\tau_{\min}, \tau_{\max}]$ để chống hội tụ sớm.  
  > Đặc biệt, nhóm thiết kế **Thuật toán Lai Memetic**: kết hợp khả năng tìm kiếm rộng của phép lai OX trong GA với khả năng tinh chỉnh sâu của `2-opt` trên từng cá thể con và phép nhiễu 4-opt Double-Bridge.  
  > Ở Slide 7, kết quả 600 lần chạy độc lập với cùng ngân sách thời gian cho thấy: Memetic đạt **chính xác 100% nghiệm tối ưu chuẩn quốc tế BKS (Best Gap = 0.00%)** trên cả 5 bộ TSPLIB (`eil51`, `berlin52`, `st70`, `eil76`, `kroA100`).  
  > Ở Slide 8, kiểm định phi tham số Friedman ($p = 6.4 \times 10^{-5}$) và kiểm định Wilcoxon phân phối chính xác đều cho $p < 0.05$, khẳng định sự vượt trội của Memetic có ý nghĩa thống kê. Khi mở rộng lên $n=1000$ đỉnh, kỹ thuật Candidate List giúp giảm thời gian 2-opt xuống chỉ còn 2 mili-giây. Sau đây em xin bấm mở trực tiếp giao diện Web Visualizer để demo quá trình hội tụ theo thời gian thực."*

---

## PHẦN 2: BỘ 8 CÂU HỎI VẤN ĐÁP GIẢNG VIÊN HAY HỎI NHẤT & CÁCH TRẢ LỜI ĂN ĐIỂM TUYỆT ĐỐI

### Câu 1: *"Em hãy chỉ cho thầy/cô chỗ nào trong code tính Delta Evaluation $\mathcal{O}(1)$ của 2-opt? Tại sao không tính lại cả chu trình?"*
- **Mở tệp:** `src/local_search.py` (dòng `18–35`, hàm `delta_2opt`).
- **Trả lời:** *"Thưa thầy/cô, khi đảo đoạn từ vị trí `i` đến `j`, chỉ có 2 cạnh cũ là `(tour[i-1], tour[i])` và `(tour[j], tour[(j+1)%n])` bị xóa đi, và thay bằng 2 cạnh mới là `(tour[i-1], tour[j])` và `(tour[i], tour[(j+1)%n])`. Hàm `delta_2opt` chỉ lấy tổng 2 cạnh mới trừ tổng 2 cạnh cũ, mất 4 phép tra ma trận $\mathcal{O}(1)$ thay vì vòng lặp $\mathcal{O}(n)$. Nhờ vậy một vòng quét lân cận giảm từ $\mathcal{O}(n^3)$ xuống $\mathcal{O}(n^2)$."*

### Câu 2: *"Tại sao trong Giải thuật Di truyền (GA), nhóm không dùng phép lai cắt 1 điểm (Single-point crossover) bình thường mà phải dùng OX và PMX?"*
- **Mở tệp:** `src/metaheuristics.py` (dòng `220–268`, hàm `order_crossover_ox` và `pmx_crossover`).
- **Trả lời:** *"Vì lời giải TSP là một **hoán vị** (mỗi thành phố phải xuất hiện đúng 1 lần). Nếu cắt nửa đầu của Cha ghép với nửa sau của Mẹ theo cách thông thường, cá thể con chắc chắn sẽ bị **lặp thành phố** này và **thiếu thành phố** kia (lời giải không hợp lệ). Phép lai OX giữ nguyên một đoạn con của Cha, rồi điền các thành phố còn thiếu theo đúng thứ tự xuất hiện bên Mẹ nên bảo toàn tính hoán vị 100%."*

### Câu 3: *"Làm sao nhóm đảm bảo tất cả các lời giải báo cáo trong bảng đều hợp lệ, không bị ăn gian hay tính nhầm độ dài?"*
- **Mở tệp:** `src/validator.py` (hàm `validate_tour` và `assert_valid_tour`).
- **Trả lời:** *"Mọi lời giải sau khi thuật toán chạy xong trong `run_experiments.py` đều bắt buộc đi qua hàm `assert_valid_tour`. Hàm này kiểm tra độc lập 3 điều kiện: (1) Độ dài mảng đúng bằng $n$, (2) Đủ mặt các đỉnh từ $0$ đến $n-1$ không trùng lặp, và (3) Cộng lại khoảng cách từ đầu theo ma trận gốc xem có khớp với chi phí thuật toán báo cáo (sai số $\le 10^{-4}$) hay không."*

### Câu 4: *"Tại sao trên các bộ dữ liệu lớn như `kroA100`, thuật toán GA thuần túy lại có sai số cao hơn hẳn SA, TS, ACO và Memetic?"*
- **Trả lời:** *"Vì GA thuần túy chỉ dựa vào lai ghép OX và đột biến ngẫu nhiên; phép lai ghép tuy ghép được các đoạn tốt từ cha mẹ nhưng tại điểm nối giữa hai đoạn thường sinh ra các cạnh chéo rất dài (thiếu khả năng khai thác cục bộ - Exploitation). Khi nhóm gắn thêm `2-opt` vào sau bước lai ghép để tạo thành **Memetic Algorithm**, các cạnh chéo tại điểm nối được gỡ ngay lập tức, giúp sai số trung bình trên `kroA100` giảm từ `4.77%` (GA) xuống chỉ còn `0.016%` (Memetic)."*

### Câu 5: *"Trong bộ dữ liệu chuẩn TSPLIB (`berlin52`, `eil51`), khoảng cách được tính như thế nào để khớp với đáp án chuẩn BKS quốc tế?"*
- **Mở tệp:** `src/tsp_instance.py` (dòng `54–62`).
- **Trả lời:** *"Theo chuẩn `EUC_2D` của TSPLIB (Reinelt, 1991), khoảng cách Euclid giữa hai điểm được làm tròn đến số nguyên gần nhất theo công thức `int(math.hypot(dx, dy) + 0.5)`. Nhóm cài đặt đúng chuẩn này nên nghiệm tối ưu tìm được trên `berlin52` khớp chính xác con số `7542` và `kroA100` khớp chính xác `21282` của thư viện TSPLIB."*

### Câu 6: *"Tại sao nhóm lại dùng kiểm định Friedman và Wilcoxon mà không dùng kiểm định t-test hay ANOVA?"*
- **Mở tệp:** `src/statistical_tests.py`.
- **Trả lời:** *"Vì dữ liệu chi phí chu trình qua nhiều bộ dữ liệu khác nhau có thang đo rất khác nhau (ví dụ `eil51` chỉ khoảng `426`, trong khi `kroA100` là `21282`) và không tuân theo phân phối chuẩn (Normal distribution). Do đó các kiểm định tham số như ANOVA hay t-test không hợp lệ; bắt buộc phải dùng kiểm định **phi tham số** dựa trên thứ hạng (Friedman Test và Wilcoxon Signed-Rank Test)."*

### Câu 7: *"Khi số đỉnh lên tới $n = 1000$, tại sao 2-opt thông thường bị chậm và nhóm đã xử lý thế nào?"*
- **Mở tệp:** `src/local_search.py` (dòng `75–125`, nhánh `use_candidate_list`).
- **Trả lời:** *"Với $n=1000$, một vòng quét 2-opt đầy đủ phải xét $\frac{1000 \times 997}{2} \approx 500\,000$ cặp cạnh. Tuy nhiên, một phép đảo đoạn 2-opt chỉ có thể giảm chi phí nếu ít nhất một cạnh mới ngắn hơn cạnh cũ. Do đó nhóm tiền xử lý **Candidate List** chỉ lưu $k=20$ láng giềng gần nhất cho mỗi đỉnh kèm cờ **Don't-Look Bits**, giảm số phép thử từ $\mathcal{O}(n^2)$ xuống $\mathcal{O}(k \cdot n)$, giúp hội tụ trên 1000 đỉnh chỉ trong `0.002 giây`."*

### Câu 8: *"Nhóm làm thế nào để đảm bảo việc so sánh 5 thuật toán Metaheuristic là công bằng?"*
- **Mở tệp:** `run_experiments.py` và `src/metaheuristics.py`.
- **Trả lời:** *"Một vòng lặp của GA hoặc ACO tốn nhiều phép tính hơn hàng nghìn lần so với một bước thử của SA. Vì vậy nếu giới hạn theo số vòng lặp sẽ không công bằng. Nhóm đã thiết lập cùng một **ngân sách thời gian thực tế (`time_limit`)** cho cả 5 thuật toán trên mỗi bộ dữ liệu, cùng xuất phát từ bộ 10 `seed` ngẫu nhiên cố định (`100..109`) và chạy trên cùng một cấu hình máy."*
