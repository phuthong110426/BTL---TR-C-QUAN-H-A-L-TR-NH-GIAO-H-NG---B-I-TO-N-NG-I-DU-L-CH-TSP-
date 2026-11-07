"""
Kịch bản chạy tự động 4 bước Demo bắt buộc khi bảo vệ theo Mục 7.2 :
(1) Chạy chương trình kiểm tra độc lập (kiemtra) trên ví dụ nhỏ của đề (vidu.txt) và berlin52.opt.tour.
(2) Chạy thuật toán chính xác (Held-Karp & Nhánh cận) + Nearest Neighbor trên ví dụ nhỏ vidu.txt (ra đúng tối ưu = 31 và NN = 33).
(3) Chạy một metaheuristic trên một thể hiện chuẩn với seed cho trước, hiển thị diễn biến giá trị tốt nhất.
(4) Tái lập một dòng trong bảng kết quả của báo cáo (theo thể hiện và seed chọn trước).
"""

import subprocess
import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PY_EXE = sys.executable


def run_step(title: str, cmd: list[str]) -> None:
    print("\n" + "#" * 78)
    print(f"# {title}")
    print(f"# Lenh: {' '.join(cmd)}")
    print("#" * 78)
    subprocess.run(cmd, cwd=ROOT_DIR, check=True)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    run_step(
        "BUOC DEMO 1A (Muc 7.2.1): Chay chuong trinh kiem tra tren vi du nho cua de (vidu.txt)",
        [PY_EXE, "kiemtra.py", "data/vidu/vidu.txt", "data/vidu/vidu.sol"],
    )
    run_step(
        "BUOC DEMO 1B (Muc 5.1 Yeu cau toi thieu): Kiem tra chu trinh toi uu berlin52.opt.tour = 7542",
        [PY_EXE, "kiemtra.py", "data/chuan/berlin52.tsp", "data/chuan/berlin52.opt.tour"],
    )
    run_step(
        "BUOC DEMO 2 (Muc 7.2.2): Chay thuat toan chinh xac & tham lam tren vi du nho vidu.txt (ra dung 31 & 33)",
        [PY_EXE, "data/vidu/de01.py"],
    )
    run_step(
        "BUOC DEMO 3 (Muc 7.2.3): Chay 1 Metaheuristic tren the hien chuan berlin52 voi seed=1001 & hien thi dien bien hoi tu",
        [PY_EXE, "solve.py", "--instance", "data/chuan/berlin52.tsp", "--algo", "MEMETIC", "--seed", "1001"],
    )
    run_step(
        "BUOC DEMO 4 (Muc 7.2.4): Tai lap 1 dong trong bang ket qua bao cao (berlin52 - Memetic - 10 seeds 1001..1010)",
        [PY_EXE, "solve.py", "--instance", "berlin52", "--algo", "MEMETIC", "--all-seeds"],
    )


if __name__ == "__main__":
    main()
