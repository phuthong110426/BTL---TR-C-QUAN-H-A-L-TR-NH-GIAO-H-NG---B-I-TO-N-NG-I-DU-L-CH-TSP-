"""
Chương trình kiểm tra độc lập tính hợp lệ của lời giải TSP (Mục 3.1.5, 5.2, 6.3 & 7.2).

Cách gọi (theo đúng Mục 5.2 & 6.3 của Đề bài tập lớn):
    python kiemtra.py <tệp_vào> <tệp_lời_giải>
hoặc trên Windows CMD/PowerShell:
    .\\kiemtra <tệp_vào> <tệp_lời_giải>

Chức năng:
1. Đọc <tệp_vào> (hỗ trợ cả định dạng tự định nghĩa dòng 1 là n, n dòng i x_i y_i và định dạng TSPLIB .tsp).
2. Đọc <tệp_lời_giải> (hỗ trợ cả định dạng .sol: dòng 1 là chi phí, dòng 2 là hoán vị n đỉnh bắt đầu từ đỉnh 1;
   và định dạng chuẩn .opt.tour của TSPLIB).
3. Kiểm tra độc lập mọi ràng buộc qua module `src/validator.py`:
   - Độ dài chu trình đúng bằng n.
   - Các đỉnh từ 1 đến n xuất hiện đúng 1 lần (không lặp đỉnh, không thiếu đỉnh).
   - Chu trình bắt đầu từ đỉnh 1 (kho xuất phát).
   - Tính lại tổng quãng đường trực tiếp từ ma trận khoảng cách EUC_2D và đối chiếu với giá trị báo cáo.
4. Báo kết quả: HOP LE / KHONG HOP LE kèm lý do chi tiết và giá trị hàm mục tiêu tính được.
"""

import os
import sys
from typing import Optional

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.tsp_instance import TSPInstance
from src.validator import validate_tour


def resolve_path(path_arg: str) -> str:
    """Tìm đường dẫn tệp nếu người dùng truyền tên ngắn gọn."""
    if os.path.exists(path_arg):
        return path_arg
    search_dirs = [
        ROOT_DIR,
        os.path.join(ROOT_DIR, "data", "vidu"),
        os.path.join(ROOT_DIR, "data", "chuan"),
        os.path.join(ROOT_DIR, "data", "tusinh"),
        os.path.join(ROOT_DIR, "data", "tsplib"),
        os.path.join(ROOT_DIR, "data", "synthetic"),
        os.path.join(ROOT_DIR, "results", "solutions"),
    ]
    for d in search_dirs:
        candidate = os.path.join(d, path_arg)
        if os.path.exists(candidate):
            return candidate
    return path_arg


def check_solution(input_file: str, solution_file: str) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    in_path = resolve_path(input_file)
    sol_path = resolve_path(solution_file)

    if not os.path.exists(in_path):
        print(f"KHONG HOP LE | Ly do: Khong tim thay tep du lieu vao '{input_file}'.")
        return 1
    if not os.path.exists(sol_path):
        print(f"KHONG HOP LE | Ly do: Khong tim thay tep loi giai '{solution_file}'.")
        return 1

    try:
        instance = TSPInstance.from_file(in_path)
    except Exception as e:
        print(f"KHONG HOP LE | Ly do: Loi doc tep du lieu vao '{in_path}': {e}")
        return 1

    reported_cost: Optional[float] = None
    is_opt_tour_format = False

    try:
        with open(sol_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
        if "TOUR_SECTION" in raw_text.upper():
            is_opt_tour_format = True
            tour_0based = TSPInstance.load_opt_tour_file(sol_path)
            tour_1based = [v + 1 for v in tour_0based]
            reported_cost = instance.bks
        else:
            reported_cost, tour_0based, tour_1based = TSPInstance.load_solution_file(sol_path)
    except Exception as e:
        print(f"KHONG HOP LE | Ly do: Loi doc tep loi giai '{sol_path}': {e}")
        return 1

    # Kiểm tra độc lập bằng hàm validate_tour (src/validator.py: dòng 11-66)
    is_valid, actual_cost, message = validate_tour(instance, tour_0based, reported_cost=reported_cost)

    # Kiểm tra quy ước bắt đầu từ đỉnh 1 đối với tệp .sol
    starts_at_one = len(tour_1based) > 0 and tour_1based[0] == 1
    if is_valid and not is_opt_tour_format and not starts_at_one:
        is_valid = False
        message = (
            f"Chu trinh hop le nhung khong bat dau tu dinh 1 (kho) theo quy uoc De 1 "
            f"(dinh dau tien hien tai la {tour_1based[0]})."
        )

    print("=" * 72)
    print("CHUONG TRINH KIEM TRA DOC LAP LOI GIAI TSP (kiemtra)")
    print("=" * 72)
    print(f"  - Tep du lieu vao : {in_path} (n = {instance.n} dinh, kieu {instance.edge_weight_type})")
    print(f"  - Tep loi giai    : {sol_path}")
    if reported_cost is not None:
        print(f"  - Gia tri bao cao : {reported_cost:.0f}" if reported_cost.is_integer() else f"  - Gia tri bao cao : {reported_cost:.4f}")
    print(f"  - Gia tri tinh lai: {actual_cost:.0f}" if abs(actual_cost - round(actual_cost)) < 1e-6 else f"  - Gia tri tinh lai: {actual_cost:.4f}")

    if instance.n <= 15 and len(tour_0based) == instance.n and is_valid:
        edges_str = []
        for k in range(instance.n):
            u = tour_0based[k]
            v = tour_0based[(k + 1) % instance.n]
            d_uv = int(instance.distance(u, v))
            edges_str.append(f"d({u+1},{v+1})={d_uv}")
        print(f"  - Chi tiet canh   : {' + '.join(edges_str)} = {int(round(actual_cost))}")

    print("-" * 72)
    if is_valid:
        print(f"KET QUA: HOP LE")
        print(f"Ly do  : {message}")
        print(f"Gia tri ham muc tieu tinh duoc: {int(round(actual_cost))}")
        print("=" * 72)
        return 0
    else:
        print(f"KET QUA: KHONG HOP LE")
        print(f"Ly do  : {message}")
        print(f"Gia tri ham muc tieu tinh duoc: {actual_cost}")
        print("=" * 72)
        return 2


def main() -> None:
    if len(sys.argv) < 3:
        print("Cach dung: python kiemtra.py <tep_vao> <tep_loi_giai>")
        print("Vi du 1  : python kiemtra.py data/vidu/vidu.txt data/vidu/vidu.sol")
        print("Vi du 2  : python kiemtra.py data/chuan/berlin52.tsp data/chuan/berlin52.opt.tour")
        sys.exit(1)
    sys.exit(check_solution(sys.argv[1], sys.argv[2]))


if __name__ == "__main__":
    main()
