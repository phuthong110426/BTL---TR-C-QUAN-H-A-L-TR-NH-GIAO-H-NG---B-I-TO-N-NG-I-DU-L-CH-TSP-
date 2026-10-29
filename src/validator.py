"""
Mục 3.1.5: Hàm kiểm tra tính hợp lệ độc lập của lời giải (Solution Validator).
Mọi lời giải của các thuật toán chính xác, tham lam, tìm kiếm cục bộ và metaheuristic
trước khi báo cáo hoặc ghi vào tệp CSV đều phải đi qua hàm kiểm tra độc lập này.
"""

from typing import List, Tuple, Optional
from .tsp_instance import TSPInstance


def validate_tour(
    instance: TSPInstance,
    tour: List[int],
    reported_cost: Optional[float] = None,
    tol: float = 1e-4,
) -> Tuple[bool, float, str]:
    """
    Kiểm tra tính hợp lệ độc lập của một chu trình TSP.

    Các điều kiện kiểm tra:
    1. Chu trình không rỗng và có đúng `n` đỉnh.
    2. Mọi phần tử trong chu trình là số nguyên thuộc tập {0, 1, ..., n - 1}.
    3. Không có đỉnh nào bị lặp lại (là một hoán vị hợp lệ của N đỉnh).
    4. Tính lại tổng chi phí chu trình trực tiếp từ ma trận khoảng cách.
    5. Nếu có `reported_cost`, kiểm tra độ lệch tuyệt đối |actual_cost - reported_cost| <= tol.

    Trả về:
        (is_valid, actual_cost, message)
    """
    n = instance.n
    if not isinstance(tour, (list, tuple)):
        return False, float("inf"), "Chu trình không phải danh sách/tuple."

    if len(tour) != n:
        return False, float("inf"), f"Sai kích thước chu trình: len(tour)={len(tour)}, kỳ vọng n={n}."

    visited = [False] * n
    for idx, node in enumerate(tour):
        if not isinstance(node, int):
            return False, float("inf"), f"Phần tử tại vị trí {idx} ({node}) không phải số nguyên."
        if node < 0 or node >= n:
            return False, float("inf"), f"Đỉnh {node} tại vị trí {idx} nằm ngoài phạm vi [0, {n - 1}]."
        if visited[node]:
            return False, float("inf"), f"Đỉnh {node} xuất hiện nhiều hơn một lần trong chu trình."
        visited[node] = True

    if not all(visited):
        return False, float("inf"), "Chu trình không đi qua đầy đủ tất cả các đỉnh."

    # Tính lại tổng độ dài chu trình độc lập
    actual_cost = 0.0
    mat = instance.dist_matrix
    for i in range(n):
        u = tour[i]
        v = tour[(i + 1) % n]
        actual_cost += mat[u][v]

    if reported_cost is not None:
        if abs(actual_cost - reported_cost) > tol:
            return (
                False,
                actual_cost,
                f"Chi phí báo cáo ({reported_cost:.4f}) không khớp với chi phí thực tế ({actual_cost:.4f}).",
            )

    return True, actual_cost, "OK"


def assert_valid_tour(
    instance: TSPInstance,
    tour: List[int],
    reported_cost: Optional[float] = None,
    algorithm_name: str = "Unknown",
) -> float:
    """
    Kiểm tra và ném ngoại lệ ValueError nếu lời giải không hợp lệ.
    Trả về chi phí thực tế đã được xác minh.
    """
    is_valid, actual_cost, msg = validate_tour(instance, tour, reported_cost)
    if not is_valid:
        raise ValueError(f"[{algorithm_name}] Lời giải KHÔNG hợp lệ trên '{instance.name}': {msg}")
    return actual_cost
