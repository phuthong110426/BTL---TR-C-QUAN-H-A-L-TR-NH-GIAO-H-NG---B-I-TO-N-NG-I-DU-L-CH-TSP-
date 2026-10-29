"""
Module vẽ biểu đồ thực nghiệm chuẩn Vector (SVG) chất lượng cao (không phụ thuộc thư viện ngoài):
1. Biểu đồ hội tụ (Convergence Curve): Giá trị hàm mục tiêu tốt nhất theo thời gian thực thi
   của cả 5 giải thuật (SA, TS, GA, ACO, Memetic) trên cùng một hệ trục.
2. Trực quan hóa lộ trình TSP (2D Tour Plot) kèm tọa độ đỉnh và tổng độ dài.
3. Biểu đồ so sánh độ lệch tương đối Gap (%) giữa các thuật toán trên các bộ dữ liệu.
"""

import os
from typing import List, Tuple, Dict, Optional
from .tsp_instance import TSPInstance

PALETTE = {
    "SA": "#E63946",       # Đỏ
    "TS": "#F4A261",       # Cam
    "GA": "#2A9D8F",       # Xanh ngọc
    "ACO": "#457B9D",      # Xanh dương
    "Memetic": "#6A0572",  # Tím đậm
    "BKS": "#1D3557",      # Xanh đen (đường đứt nét)
}


def save_convergence_svg(
    filepath: str,
    instance_name: str,
    curves: Dict[str, List[Tuple[float, int, float]]],
    bks: Optional[float] = None,
    width: int = 820,
    height: int = 460,
) -> None:
    """
    Vẽ đường hội tụ (giá trị tốt nhất theo thời gian giây) của các thuật toán trên cùng biểu đồ SVG.
    Mỗi phần tử trong `curves[alg_name]` là danh sách `(time_sec, iter, best_cost)`.
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    pad_left, pad_right, pad_top, pad_bottom = 85, 165, 55, 60
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    all_times = [pt[0] for seq in curves.values() for pt in seq]
    all_costs = [pt[2] for seq in curves.values() for pt in seq]
    if bks is not None:
        all_costs.append(bks)

    max_t = max(all_times) if all_times else 1.0
    if max_t <= 1e-6:
        max_t = 1.0
    min_c = min(all_costs) * 0.98 if all_costs else 0.0
    max_c = max(all_costs) * 1.02 if all_costs else 100.0
    if abs(max_c - min_c) < 1e-6:
        max_c = min_c + 10.0

    def tx(t: float) -> float:
        return pad_left + (min(t, max_t) / max_t) * plot_w

    def ty(c: float) -> float:
        return pad_top + plot_h - ((c - min_c) / (max_c - min_c)) * plot_h

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#ffffff; font-family:Segoe UI, Arial, sans-serif;">',
        f'<rect width="{width}" height="{height}" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>',
        f'<text x="{width/2 - 30:.1f}" y="30" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e293b">Đường hội tụ theo thời gian - Thể hiện: {instance_name}</text>',
    ]

    # Lưới ngang và nhãn trục Y
    num_y_ticks = 6
    for i in range(num_y_ticks + 1):
        val = min_c + (max_c - min_c) * (i / num_y_ticks)
        y = ty(val)
        lines.append(f'<line x1="{pad_left}" y1="{y:.1f}" x2="{pad_left + plot_w}" y2="{y:.1f}" stroke="#f1f5f9" stroke-width="1"/>')
        lines.append(f'<text x="{pad_left - 10}" y="{y + 4:.1f}" text-anchor="end" font-size="11" fill="#475569">{val:.0f}</text>')

    # Lưới dọc và nhãn trục X
    num_x_ticks = 5
    for i in range(num_x_ticks + 1):
        val = max_t * (i / num_x_ticks)
        x = tx(val)
        lines.append(f'<line x1="{x:.1f}" y1="{pad_top}" x2="{x:.1f}" y2="{pad_top + plot_h}" stroke="#f1f5f9" stroke-width="1"/>')
        lines.append(f'<text x="{x:.1f}" y="{pad_top + plot_h + 20}" text-anchor="middle" font-size="11" fill="#475569">{val:.2f}s</text>')

    # Khung trục
    lines.append(f'<rect x="{pad_left}" y="{pad_top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#94a3b8" stroke-width="1.5"/>')
    lines.append(f'<text x="{pad_left + plot_w/2:.1f}" y="{height - 15}" text-anchor="middle" font-size="13" font-weight="600" fill="#334155">Thời gian chạy (giây)</text>')
    lines.append(f'<text x="22" y="{pad_top + plot_h/2:.1f}" text-anchor="middle" font-size="13" font-weight="600" fill="#334155" transform="rotate(-90, 22, {pad_top + plot_h/2:.1f})">Chi phí chu trình tốt nhất f(s)</text>')

    # Đường BKS / Optimal nếu có
    if bks is not None:
        yb = ty(bks)
        lines.append(f'<line x1="{pad_left}" y1="{yb:.1f}" x2="{pad_left + plot_w}" y2="{yb:.1f}" stroke="#1D3557" stroke-width="1.8" stroke-dasharray="6,4"/>')
        lines.append(f'<text x="{pad_left + 8}" y="{yb - 6:.1f}" font-size="11" font-weight="bold" fill="#1D3557">BKS / Optimal = {bks:.0f}</text>')

    # Vẽ đường hội tụ của từng thuật toán và chú giải (Legend)
    legend_x = pad_left + plot_w + 18
    legend_y = pad_top + 15

    for idx, (alg_name, seq) in enumerate(curves.items()):
        if not seq:
            continue
        color = PALETTE.get(alg_name, "#3b82f6")
        pts_str = " ".join(f"{tx(pt[0]):.1f},{ty(pt[2]):.1f}" for pt in seq)
        lines.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.4" points="{pts_str}"/>')

        # Chấm tròn ở điểm đầu và điểm cuối
        x_end, y_end = tx(seq[-1][0]), ty(seq[-1][2])
        lines.append(f'<circle cx="{x_end:.1f}" cy="{y_end:.1f}" r="3.5" fill="{color}"/>')

        # Mục Legend
        ly = legend_y + idx * 28
        lines.append(f'<line x1="{legend_x}" y1="{ly}" x2="{legend_x + 22}" y2="{ly}" stroke="{color}" stroke-width="3"/>')
        lines.append(f'<circle cx="{legend_x + 11}" cy="{ly}" r="3.5" fill="{color}"/>')
        lines.append(f'<text x="{legend_x + 30}" y="{ly + 4}" font-size="12" font-weight="600" fill="#1e293b">{alg_name} ({seq[-1][2]:.0f})</text>')

    lines.append("</svg>")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def save_tour_svg(
    filepath: str,
    instance: TSPInstance,
    tour: List[int],
    alg_name: str,
    cost: float,
    width: int = 640,
    height: int = 580,
) -> None:
    """Vẽ sơ đồ chu trình TSP trên mặt phẳng tọa độ 2D ra tệp SVG."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    pad = 55
    plot_w = width - 2 * pad
    plot_h = height - 2 * pad - 20

    xs = [c[0] for c in instance.coords]
    ys = [c[1] for c in instance.coords]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(1e-6, max_x - min_x)
    span_y = max(1e-6, max_y - min_y)

    def px(x: float) -> float:
        return pad + ((x - min_x) / span_x) * plot_w

    def py(y: float) -> float:
        return pad + 20 + plot_h - ((y - min_y) / span_y) * plot_h

    bks_str = f" | BKS: {instance.bks:.0f} (Gap: {(cost - instance.bks)/instance.bks*100:.2f}%)" if instance.bks else ""
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#ffffff; font-family:Segoe UI, Arial, sans-serif;">',
        f'<rect width="{width}" height="{height}" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>',
        f'<text x="{width/2:.1f}" y="30" text-anchor="middle" font-size="15" font-weight="bold" fill="#0f172a">Lộ trình {instance.name} ({alg_name}) - Chi phí: {cost:.0f}{bks_str}</text>',
        f'<rect x="{pad - 15}" y="{pad + 5}" width="{plot_w + 30}" height="{plot_h + 30}" fill="#f8fafc" stroke="#e2e8f0" rx="6"/>',
    ]

    # Vẽ các cạnh của chu trình
    pts = [f"{px(instance.coords[u][0]):.1f},{py(instance.coords[u][1]):.1f}" for u in tour]
    pts.append(pts[0])
    lines.append(f'<polyline fill="none" stroke="#2563eb" stroke-width="2.0" stroke-opacity="0.85" points="{" ".join(pts)}"/>')

    # Vẽ các đỉnh
    for idx, u in enumerate(tour):
        cx = px(instance.coords[u][0])
        cy = py(instance.coords[u][1])
        if idx == 0:
            lines.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6.5" fill="#dc2626" stroke="#ffffff" stroke-width="1.5"/>')
            lines.append(f'<text x="{cx + 8:.1f}" y="{cy - 6:.1f}" font-size="11" font-weight="bold" fill="#dc2626">Kho (#{u+1})</text>')
        else:
            lines.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.0" fill="#1e293b" stroke="#ffffff" stroke-width="1"/>')
            if instance.n <= 60:
                lines.append(f'<text x="{cx + 5:.1f}" y="{cy - 4:.1f}" font-size="9" fill="#475569">{u+1}</text>')

    lines.append("</svg>")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
