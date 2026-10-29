"""
Mục 2.2 & Mục 6: Kiểm định thống kê phi tham số (Non-parametric Statistical Tests)
cho đánh giá thực nghiệm các giải thuật Metaheuristic (Derrac et al., 2011):
1. Kiểm định dấu hạng Wilcoxon (Wilcoxon Signed-Rank Test) so sánh cặp thuật toán.
2. Kiểm định Friedman (Friedman Test) & Iman-Davenport xếp hạng nhiều thuật toán trên tập thể hiện.
Cài đặt thuần Python chuẩn (không phụ thuộc thư viện ngoài), tính p-value chính xác.
"""

import math
from typing import List, Dict, Tuple


def _normal_cdf(z: float) -> float:
    """Hàm phân phối tích lũy chuẩn tắc Phi(z) sử dụng math.erf."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _chi2_survival(x: float, df: int) -> float:
    """
    Xấp xỉ Wilson-Hilferty độ chính xác cao cho p-value = P(Chi^2_df >= x).
    """
    if x <= 0.0 or df <= 0:
        return 1.0
    if df == 1:
        return 2.0 * (1.0 - _normal_cdf(math.sqrt(x)))
    if df == 2:
        return math.exp(-0.5 * x)
    k = float(df)
    z = ((x / k) ** (1.0 / 3.0) - (1.0 - 2.0 / (9.0 * k))) / math.sqrt(2.0 / (9.0 * k))
    return max(0.0, min(1.0, 1.0 - _normal_cdf(z)))


def wilcoxon_signed_rank(
    x: List[float],
    y: List[float],
) -> Dict[str, float]:
    """
    Thực hiện kiểm định dấu hạng Wilcoxon (Wilcoxon Signed-Rank Test) hai phía
    trên hai mẫu ghép cặp `x` và `y` (ví dụ: chi phí trung bình của 2 thuật toán trên N thể hiện
    hoặc trên 10-30 lần chạy cùng seed).

    Trả về dict gồm:
        w_plus: Tổng hạng dương (x > y, tức y tốt hơn x đối với bài toán cực tiểu)
        w_minus: Tổng hạng âm (x < y, tức x tốt hơn y)
        w_stat: min(w_plus, w_minus)
        z_score: Thống kê chuẩn hóa Z (có hiệu chỉnh đồng hạng - tie correction)
        p_value: Giá trị p hai phía (two-tailed); tính CHÍNH XÁC khi n_effective <= 30,
                 xấp xỉ chuẩn (có hiệu chỉnh liên tục) khi n_effective > 30
        n_effective: Số cặp có độ chênh lệch khác 0
        method: 'exact' hoặc 'normal'
    """
    if len(x) != len(y):
        raise ValueError("Hai mẫu x và y phải có cùng kích thước.")

    diffs = [xi - yi for xi, yi in zip(x, y) if abs(xi - yi) > 1e-9]
    n = len(diffs)
    if n == 0:
        return {
            "w_plus": 0.0,
            "w_minus": 0.0,
            "w_stat": 0.0,
            "z_score": 0.0,
            "p_value": 1.0,
            "n_effective": 0,
            "method": "none",
        }

    # Sắp xếp theo trị tuyệt đối |d_i| để gán hạng (xử lý đồng hạng bằng hạng trung bình)
    indexed = sorted(enumerate(diffs), key=lambda item: abs(item[1]))
    ranks = [0.0] * n
    tie_counts: List[int] = []

    i = 0
    while i < n:
        j = i
        val = abs(indexed[i][1])
        while j < n and abs(abs(indexed[j][1]) - val) <= 1e-9:
            j += 1
        # Các phần tử từ i đến j-1 có cùng trị tuyệt đối -> hạng từ (i+1) đến j
        avg_rank = 0.5 * ((i + 1) + j)
        for k in range(i, j):
            ranks[k] = avg_rank
        if j - i > 1:
            tie_counts.append(j - i)
        i = j

    w_plus = 0.0
    w_minus = 0.0
    for k in range(n):
        orig_diff = indexed[k][1]
        if orig_diff > 0:
            w_plus += ranks[k]
        else:
            w_minus += ranks[k]

    w_stat = min(w_plus, w_minus)
    mean_w = n * (n + 1.0) / 4.0
    tie_corr = sum(t * (t * t - 1.0) for t in tie_counts) / 48.0
    var_w = (n * (n + 1.0) * (2.0 * n + 1.0)) / 24.0 - tie_corr

    if var_w <= 1e-12:
        z_score = 0.0
    else:
        z_score = max(0.0, (abs(w_stat - mean_w) - 0.5) / math.sqrt(var_w))

    if n <= 30:
        # P-value CHÍNH XÁC (exact) bằng quy hoạch động trên phân phối của W+ dưới H0:
        # mỗi hạng r_k mang dấu +/- với xác suất 1/2 độc lập. Hạng trung bình khi đồng hạng
        # là bội của 0.5 nên nhân đôi để làm việc với số nguyên.
        int_ranks = [int(round(2 * r)) for r in ranks]
        total = sum(int_ranks)
        dist = [0] * (total + 1)
        dist[0] = 1
        for r in int_ranks:
            for s in range(total, r - 1, -1):
                dist[s] += dist[s - r]
        w2 = int(round(2 * w_stat))
        p_val = min(1.0, 2.0 * sum(dist[: w2 + 1]) / float(2 ** n))
        method = "exact"
    else:
        p_val = 2.0 * (1.0 - _normal_cdf(z_score)) if var_w > 1e-12 else 1.0
        method = "normal"

    return {
        "w_plus": round(w_plus, 3),
        "w_minus": round(w_minus, 3),
        "w_stat": round(w_stat, 3),
        "z_score": round(z_score, 4),
        "p_value": round(p_val, 6),
        "n_effective": n,
        "method": method,
    }


def friedman_test(
    alg_names: List[str],
    performance_matrix: List[List[float]],
) -> Dict[str, object]:
    """
    Thực hiện kiểm định Friedman (Friedman Test) cho k thuật toán trên N thể hiện (instances).
    - `alg_names`: danh sách tên k thuật toán.
    - `performance_matrix`: ma trận kích thước N x k, trong đó hàng i là kết quả (ví dụ: mean cost)
      của k thuật toán trên thể hiện thứ i (giá trị nhỏ hơn được xếp hạng cao hơn: hạng 1 là tốt nhất).

    Trả về dict gồm:
        avg_ranks: Dict[alg_name, average_rank]
        chi2_stat: Thống kê Friedman Chi^2_F với (k - 1) bậc tự do
        f_stat: Thống kê Iman-Davenport F_F
        p_value: Giá trị p của kiểm định Friedman
        instance_ranks: Ma trận hạng trên từng thể hiện
    """
    n_inst = len(performance_matrix)
    k = len(alg_names)
    if n_inst == 0 or k < 2:
        raise ValueError("Cần ít nhất 1 thể hiện và 2 thuật toán để chạy kiểm định Friedman.")

    instance_ranks: List[List[float]] = []
    rank_sums = [0.0] * k

    for row in performance_matrix:
        if len(row) != k:
            raise ValueError("Số cột trong performance_matrix không khớp với số thuật toán.")
        # Sắp xếp chỉ số theo giá trị tăng dần (nhỏ nhất -> hạng 1)
        order = sorted(range(k), key=lambda idx: row[idx])
        ranks = [0.0] * k
        i = 0
        while i < k:
            j = i
            while j < k and abs(row[order[j]] - row[order[i]]) <= 1e-9:
                j += 1
            avg_r = 0.5 * ((i + 1) + j)
            for m in range(i, j):
                ranks[order[m]] = avg_r
            i = j

        instance_ranks.append(ranks)
        for idx in range(k):
            rank_sums[idx] += ranks[idx]

    avg_ranks = {alg_names[idx]: round(rank_sums[idx] / n_inst, 4) for idx in range(k)}
    sum_sq_ranks = sum((r_sum / n_inst) ** 2 for r_sum in rank_sums)

    chi2_f = (12.0 * n_inst / (k * (k + 1.0))) * (sum_sq_ranks - (k * ((k + 1.0) ** 2)) / 4.0)
    chi2_f = max(0.0, chi2_f)

    denom = n_inst * (k - 1.0) - chi2_f
    if denom > 1e-9:
        f_stat = ((n_inst - 1.0) * chi2_f) / denom
    else:
        f_stat = float("inf")

    p_val = _chi2_survival(chi2_f, k - 1)

    return {
        "avg_ranks": avg_ranks,
        "chi2_stat": round(chi2_f, 4),
        "f_stat": round(f_stat, 4),
        "df": k - 1,
        "n_instances": n_inst,
        "p_value": round(p_val, 6),
        "instance_ranks": instance_ranks,
    }
