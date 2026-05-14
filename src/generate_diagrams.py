"""
Generate explanatory diagrams for the Memetic Algorithm VRP documentation.
Run with: python generate_diagrams.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc, Circle, Wedge
import numpy as np

# ── Style ────────────────────────────────────────────────────────────────────
plt.rcParams["font.size"] = 11
plt.rcParams["font.family"] = "DejaVu Sans"
COLORS = {
    "ga": "#4363d8",
    "ls": "#e6194b",
    "elite": "#3cb44b",
    "depot": "#000000",
    "customer": "#f58231",
    "route": "#42d4f4",
    "bg": "#f8f9fa",
    "text": "#333333",
    "arrow": "#666666",
}


def draw_rounded_box(ax, x, y, w, h, color, text, text_color="white", fs=10):
    """Draw a rounded rectangle with text."""
    box = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                         boxstyle="round,pad=0.15", facecolor=color,
                         edgecolor="black", linewidth=1.2)
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            fontweight="bold", color=text_color)


def draw_arrow(ax, x1, y1, x2, y2, color="#666666"):
    """Draw an arrow between two points."""
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color, lw=2))


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGRAM 1: Memetic Algorithm Flowchart
# ═══════════════════════════════════════════════════════════════════════════════

def diagram_flowchart():
    fig, ax = plt.subplots(1, 1, figsize=(12, 13))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.axis("off")
    ax.set_facecolor("#f8f9fa")

    # Title
    ax.text(5, 13.5, "Memetic Algorithm for VRP", ha="center", fontsize=18,
            fontweight="bold", color="#1a1a2e")

    y_positions = [12.0, 10.5, 9.2, 8.0, 6.7, 5.4, 4.1, 2.8, 1.5]

    # Boxes - left column (GA)
    draw_rounded_box(ax, 2.5, y_positions[0], 3.5, 1.0, "#4363d8",
                     "INITIALIZE\nRandom Population", fs=9)
    draw_rounded_box(ax, 2.5, y_positions[1], 3.5, 1.0, "#4363d8",
                     "EVALUATE\nFitness (Prins Split)", fs=9)
    draw_rounded_box(ax, 2.5, y_positions[2], 3.5, 1.0, "#4363d8",
                     "SELECTION\nTournament", fs=9)
    draw_rounded_box(ax, 2.5, y_positions[3], 3.5, 1.0, "#4363d8",
                     "CROSSOVER\nOrder Crossover (OX)", fs=9)
    draw_rounded_box(ax, 2.5, y_positions[4], 3.5, 1.0, "#4363d8",
                     "MUTATION\nSwap / Inversion / Displacement", fs=9)

    # Boxes - right column (Local Search)
    draw_rounded_box(ax, 7.5, y_positions[5], 3.5, 1.0, "#e6194b",
                     "LOCAL SEARCH (Memetic)\nDecode → Improve → Rebuild", fs=9)

    # Boxes - bottom (shared)
    draw_rounded_box(ax, 5, y_positions[6], 4.0, 1.0, "#3cb44b",
                     "ELITISM + REPLACE\nPreserve best, update population", fs=9)
    draw_rounded_box(ax, 5, y_positions[7], 4.0, 1.0, "#ffa500",
                     "DIVERSITY INJECTION\nIf stagnating, add random tours", fs=9)
    draw_rounded_box(ax, 5, y_positions[8], 3.0, 0.8, "#333333",
                     "TERMINATE?\nReturn best solution", fs=9)

    # Arrows - left column
    for i in range(4):
        draw_arrow(ax, 2.5, y_positions[i] - 0.5, 2.5, y_positions[i + 1] + 0.5)

    # Arrow from last GA box to Local Search
    draw_arrow(ax, 2.5, y_positions[4] - 0.5, 5.0, y_positions[5] + 0.5)
    # Label
    ax.annotate("Offspring", xy=(3.2, y_positions[4] - 0.7), fontsize=8,
                color="#666666", ha="center")

    # Arrow from Local Search to Elitism
    draw_arrow(ax, 7.5, y_positions[5] - 0.5, 6.5, y_positions[6] + 0.5)
    # Also show interaction: replace worst
    draw_arrow(ax, 7.5, y_positions[5] - 0.5, 5.0, y_positions[6] + 0.5)

    # Arrows - bottom
    draw_arrow(ax, 5, y_positions[6] - 0.5, 5, y_positions[7] + 0.5)
    draw_arrow(ax, 5, y_positions[7] - 0.5, 5, y_positions[8] + 0.5)

    # Loop arrow from termination back to evaluate
    ax.annotate("Next Generation\n(if not terminated)", xy=(1.0, y_positions[1]),
                xytext=(1.0, y_positions[8] - 0.4),
                arrowprops=dict(arrowstyle="->", color="#888888", lw=1.5,
                                connectionstyle="arc3,rad=-0.3"),
                fontsize=8, color="#888888", ha="center")
    ax.annotate("Next Gen", xy=(3.5, 12.3), fontsize=7, color="#888888")

    # Legend
    legend_elements = [
        mpatches.Patch(color="#4363d8", label="Genetic Algorithm (Global Search)"),
        mpatches.Patch(color="#e6194b", label="Local Search (Memetic Refinement)"),
        mpatches.Patch(color="#3cb44b", label="Population Management"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=8,
              framealpha=0.9)

    plt.tight_layout()
    plt.savefig("../diagrams/diagram_flowchart.png", dpi=150, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("  [OK] diagram_flowchart.png")


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGRAM 2: Giant Tour Encoding + Prins Split
# ═══════════════════════════════════════════════════════════════════════════════

def diagram_encoding():
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor("white")

    titles = ["Step 1: Giant Tour (Chromosome)",
              "Step 2: Prins Split (Decoding)",
              "Step 3: Feasible Routes (Solution)"]

    # ── Step 1: Giant Tour ──
    ax = axes[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_title(titles[0], fontsize=13, fontweight="bold", pad=12)

    tour = [3, 7, 1, 5, 9, 2, 8, 4, 6, 10]
    colors_map = ["#e6194b", "#e6194b", "#3cb44b", "#3cb44b", "#3cb44b",
                  "#4363d8", "#4363d8", "#4363d8", "#4363d8", "#ffe119"]
    labels_map = ["V1", "V1", "V2", "V2", "V2", "V3", "V3", "V3", "V3", "V4"]

    for i, (c, col) in enumerate(zip(tour, colors_map)):
        x = 1 + (i % 5) * 1.8
        y = 7 - (i // 5) * 1.5
        circle = Circle((x, y), 0.55, facecolor=col, edgecolor="black", linewidth=1.5)
        ax.add_patch(circle)
        ax.text(x, y, str(c), ha="center", va="center", fontsize=10,
                fontweight="bold", color="white")
        if i < len(tour) - 1:
            ax.annotate("", xy=(1 + ((i + 1) % 5) * 1.8, 7 - ((i + 1) // 5) * 1.5),
                        xytext=(x + 0.55, y),
                        arrowprops=dict(arrowstyle="->", color="#888", lw=1.2))
            if i == 4:  # wrap
                ax.annotate("", xy=(1, 5.5), xytext=(x + 0.55, y),
                            arrowprops=dict(arrowstyle="->", color="#888", lw=1.2,
                                            connectionstyle="arc3,rad=0.3"))

    ax.text(5, 1.5, "Permutation of all customers\n(1D array, no depot)",
            ha="center", fontsize=9, color="#555",
            bbox=dict(boxstyle="round", facecolor="#f0f0f0", alpha=0.8))

    # ── Step 2: Prins Split ──
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_title(titles[1], fontsize=13, fontweight="bold", pad=12)

    # Show the DP graph
    ax.text(5, 7.5, "Shortest Path on Auxiliary Graph", ha="center", fontsize=10,
            fontweight="bold", color="#333")

    # Nodes 0 to n
    nodes = list(range(len(tour) + 1))
    for i in nodes:
        x_pos = 0.5 + i * 0.85
        circle = Circle((x_pos, 6), 0.25, facecolor="white",
                        edgecolor="black", linewidth=1.5)
        ax.add_patch(circle)
        ax.text(x_pos, 6, str(i), ha="center", va="center", fontsize=8,
                fontweight="bold")

    # Edges (simplified - show only the optimal path edges)
    optimal_edges = [(0, 2), (2, 5), (5, 8), (8, 10)]
    all_edges = []
    for i in range(len(tour)):
        cum_dem = 0
        for j in range(i, len(tour)):
            cum_dem += np.random.randint(1, 5)  # simplified
            if cum_dem <= 80:  # capacity
                all_edges.append((i, j + 1))

    # Draw optimal path edges
    for (i, j) in optimal_edges:
        x1, x2 = 0.5 + i * 0.85, 0.5 + j * 0.85
        ax.annotate("", xy=(x2, 6), xytext=(x1, 6),
                    arrowprops=dict(arrowstyle="->", color="#e6194b", lw=2.5))
        # Label edge
        mid_x = (x1 + x2) / 2
        ax.text(mid_x, 5.3, f"dist:{40 + i * 10}", ha="center", fontsize=5.5,
                color="#e6194b")

    # Draw some other edges in grey
    for (i, j) in [(0, 3), (2, 4), (5, 7), (8, 9)]:
        x1, x2 = 0.5 + i * 0.85, 0.5 + j * 0.85
        ax.plot([x1, x2], [6, 5.7], color="#cccccc", linewidth=0.5)

    ax.text(5, 3.5, "DP finds the minimum-cost\npartition respecting capacity",
            ha="center", fontsize=9, color="#555",
            bbox=dict(boxstyle="round", facecolor="#f0f0f0", alpha=0.8))

    # ── Step 3: Routes ──
    ax = axes[2]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_title(titles[2], fontsize=13, fontweight="bold", pad=12)

    # Depot
    ax.scatter([5], [7], c="black", s=200, marker="s", zorder=10)
    ax.text(5, 6.5, "DEPOT", ha="center", fontsize=8, fontweight="bold")

    route_data = [
        {"customers": [(3, 6), (5, 5.5)], "color": "#e6194b", "label": "R1: 3→7"},
        {"customers": [(2, 5), (4, 4.5), (6, 4)], "color": "#3cb44b", "label": "R2: 1→5→9"},
        {"customers": [(4, 3), (6, 2.5), (8, 2)], "color": "#4363d8", "label": "R3: 2→8→4→6"},
    ]

    for rdata in route_data:
        col = rdata["color"]
        pts = np.array([(5, 7)] + rdata["customers"] + [(5, 7)])
        ax.plot(pts[:, 0], pts[:, 1], "-", color=col, linewidth=2, alpha=0.8)
        for (cx, cy) in rdata["customers"]:
            ax.scatter(cx, cy, c=col, s=80, zorder=5, edgecolors="black")

    ax.text(5, 1.0, "Each route: depot → ... → depot\nTotal demand ≤ vehicle capacity",
            ha="center", fontsize=9, color="#555",
            bbox=dict(boxstyle="round", facecolor="#f0f0f0", alpha=0.8))

    plt.tight_layout()
    plt.savefig("../diagrams/diagram_encoding.png", dpi=150, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("  [OK] diagram_encoding.png")


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGRAM 3: Local Search Operators
# ═══════════════════════════════════════════════════════════════════════════════

def diagram_local_search():
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.patch.set_facecolor("white")

    operators = [
        ("2-opt (Intra-route)",
         "Reverse a subtour to eliminate crossings\nRed edges removed, green edges added",
         "intra"),
        ("Or-opt (Intra-route)",
         "Relocate a segment of k nodes\nwithin the same route",
         "intra"),
        ("Relocate (Inter-route)",
         "Move one customer from Route A to Route B\nat the best insertion position",
         "inter"),
        ("2-opt* (Inter-route)",
         "Cross two routes at split points and reconnect\nA→A[0:i]+B[j:]   B→B[0:j]+A[i:]",
         "inter"),
    ]

    for idx, (ax, (title, desc, op_type)) in enumerate(zip(axes.flat, operators)):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.axis("off")
        ax.set_title(title, fontsize=13, fontweight="bold", pad=8)

        if idx == 0:  # 2-opt
            # Before
            pts_before = [(2, 1), (3, 4), (5, 5), (7, 4), (8, 1)]
            for i, (px, py) in enumerate(pts_before):
                ax.scatter(px, py, c="#4363d8", s=60, zorder=5, edgecolors="black")
                ax.text(px + 0.15, py + 0.15, str(i + 1), fontsize=8)
            # Cross - draw crossing lines in red
            ax.plot([pts_before[1][0], pts_before[2][0]],
                    [pts_before[1][1], pts_before[2][1]], "r-", linewidth=3, alpha=0.6)
            ax.plot([pts_before[2][0], pts_before[3][0]],
                    [pts_before[2][1], pts_before[3][1]], "r-", linewidth=3, alpha=0.6)
            ax.plot([pts_before[3][0], pts_before[4][0]],
                    [pts_before[3][1], pts_before[4][1]], "r-", linewidth=3, alpha=0.6)
            # Other edges in grey
            ax.plot([pts_before[0][0], pts_before[1][0]],
                    [pts_before[0][1], pts_before[1][1]], "gray", linewidth=1.5)
            ax.plot([pts_before[4][0], pts_before[0][0]],
                    [pts_before[4][1], pts_before[0][1]], "gray", linewidth=1.5)
            ax.text(5, 6.5, "Before: crossed edges waste distance", ha="center",
                    fontsize=9, color="#e6194b")

            # After - show correction with green arrows
            ax.annotate("", xy=(6, 5.5), xytext=(1.5, 5.8),
                        arrowprops=dict(arrowstyle="->", color="green", lw=2))
            ax.text(1.5, 6.8, "After 2-opt:", fontsize=9, fontweight="bold", color="green")

            # Sub-figure: after
            for i, (px, py) in enumerate(pts_before):
                ax.scatter(px - 0.3, py, c="#3cb44b", s=60, zorder=5, edgecolors="black",
                           alpha=0.5)

        elif idx == 1:  # Or-opt
            # Route visualization
            pts = [(1, 4), (3, 5), (5, 5), (7, 4.5), (9, 3)]
            for i, (px, py) in enumerate(pts):
                ax.scatter(px, py, c="#4363d8", s=60, zorder=5, edgecolors="black")
                ax.text(px + 0.2, py + 0.15, str(i + 1), fontsize=9)
            ax.plot([p[0] for p in pts], [p[1] for p in pts], "gray", linewidth=2)

            # Highlight segment 2-3-4
            ax.plot([pts[1][0], pts[2][0], pts[3][0]],
                    [pts[1][1], pts[2][1], pts[3][1]], "#e6194b", linewidth=4, alpha=0.7)
            ax.annotate("", xy=(3.5, 2.5), xytext=(3.5, 3.5),
                        arrowprops=dict(arrowstyle="->", color="green", lw=2))
            ax.text(5, 2, "Segment [2,3,4] moved\nfrom pos 2 to pos 5",
                    ha="center", fontsize=9, color="#333",
                    bbox=dict(boxstyle="round", facecolor="#f0f0f0", alpha=0.8))

        elif idx == 2:  # Relocate
            # Two routes
            r1_pts = [(1, 6), (3, 6.5), (5, 6)]
            r2_pts = [(7, 5), (9, 4.5), (8, 3.5), (6, 3)]
            for i, (px, py) in enumerate(r1_pts):
                ax.scatter(px, py, c="#e6194b", s=60, zorder=5, edgecolors="black")
            for i, (px, py) in enumerate(r2_pts):
                ax.scatter(px, py, c="#4363d8", s=60, zorder=5, edgecolors="black")
            ax.plot([p[0] for p in r1_pts], [p[1] for p in r1_pts],
                    "#e6194b", linewidth=2, alpha=0.6)
            ax.plot([p[0] for p in r2_pts], [p[1] for p in r2_pts],
                    "#4363d8", linewidth=2, alpha=0.6)

            # Highlight node to move
            ax.scatter(*r1_pts[1], c="yellow", s=120, zorder=6, edgecolors="black", linewidth=2)

            # Arrow showing the move
            ax.annotate("", xy=(r2_pts[0][0] + 0.3, r2_pts[0][1] + 1.0),
                        xytext=(r1_pts[1][0], r1_pts[1][1] - 0.5),
                        arrowprops=dict(arrowstyle="->", color="green", lw=2.5,
                                        connectionstyle="arc3,rad=0.3"))
            ax.text(5, 1.5, "Customer moves from route A to route B\nRedistributing demand",
                    ha="center", fontsize=9,
                    bbox=dict(boxstyle="round", facecolor="#f0f0f0", alpha=0.8))

        elif idx == 3:  # 2-opt*
            r1 = [(1, 6), (3, 6.5), (5, 6)]
            r2 = [(7, 5), (8, 3.5), (6, 3)]
            for i, (px, py) in enumerate(r1):
                ax.scatter(px, py, c="#e6194b", s=60, zorder=5, edgecolors="black")
            for i, (px, py) in enumerate(r2):
                ax.scatter(px, py, c="#4363d8", s=60, zorder=5, edgecolors="black")
            ax.plot([p[0] for p in r1], [p[1] for p in r1],
                    "#e6194b", linewidth=2, alpha=0.6)
            ax.plot([p[0] for p in r2], [p[1] for p in r2],
                    "#4363d8", linewidth=2, alpha=0.6)

            # Show cross point
            ax.scatter(*r1[1], c="white", s=200, zorder=7, edgecolors="green", linewidth=2)
            ax.scatter(*r2[0], c="white", s=200, zorder=7, edgecolors="green", linewidth=2)
            ax.plot([r1[1][0], r2[0][0]], [r1[1][1], r2[0][1]], "g--", linewidth=2, alpha=0.8)

            ax.text(5, 1.5, "Route A[0:i] + Route B[j:]\nRoute B[0:j] + Route A[i:]",
                    ha="center", fontsize=9,
                    bbox=dict(boxstyle="round", facecolor="#f0f0f0", alpha=0.8))

        ax.text(5, 0.3, desc, ha="center", fontsize=8.5, color="#777")

    fig.suptitle("Local Search Operators in Memetic Algorithm",
                 fontsize=15, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig("../diagrams/diagram_local_search.png", dpi=150, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("  [OK] diagram_local_search.png")


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGRAM 4: Architecture Overview
# ═══════════════════════════════════════════════════════════════════════════════

def diagram_architecture():
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 12)
    ax.axis("off")
    ax.set_facecolor("#f8f9fa")

    ax.text(6, 11.5, "Memetic Algorithm for VRP — Architecture", ha="center",
            fontsize=16, fontweight="bold", color="#1a1a2e")

    # ── Input Layer ──
    draw_rounded_box(ax, 6, 10.2, 8, 1.0, "#e8e8e8",
                     "INPUT: VRP Instance (Depot, Customers, Demands, Vehicle Capacity, Fleet Size)",
                     text_color="#333", fs=9)

    # ── GA Layer ──
    ax.text(3, 8.5, "Genetic Algorithm", ha="center", fontsize=13, fontweight="bold",
            color="#4363d8")
    draw_rounded_box(ax, 1.8, 7.5, 2.5, 0.8, "#4363d8", "Population\n(Random Tours)", fs=8)
    draw_rounded_box(ax, 4.8, 7.5, 2.5, 0.8, "#4363d8", "Selection &\nCrossover (OX)", fs=8)

    draw_arrow(ax, 3.0, 7.1, 3.6, 7.1)

    # ── Decoding ──
    draw_rounded_box(ax, 6, 6.2, 3.0, 1.0, "#f58231",
                     "Prins Split\nDecoding", fs=9)
    draw_arrow(ax, 4.8, 7.1, 5.5, 6.7)

    # ── LS Layer ──
    ax.text(9, 8.5, "Local Search (Memetic)", ha="center", fontsize=13, fontweight="bold",
            color="#e6194b")
    draw_rounded_box(ax, 8.5, 7.5, 2.5, 0.8, "#e6194b", "2-opt\nOr-opt", fs=8)
    draw_rounded_box(ax, 11, 7.5, 2.5, 0.8, "#e6194b", "Relocate\nExchange\n2-opt*", fs=8)

    # Labels
    ax.text(8.5, 8.5, "Intra-route", ha="center", fontsize=8, color="#e6194b")
    ax.text(11, 8.5, "Inter-route", ha="center", fontsize=8, color="#e6194b")

    draw_arrow(ax, 7.2, 6.7, 8.5, 7.1)
    draw_arrow(ax, 7.2, 6.7, 11, 7.1)

    # From LS back to decode
    draw_rounded_box(ax, 9.8, 5.0, 3.0, 1.2, "#ffa500",
                     "Rebuild Giant Tour\n(from improved routes)", fs=8)

    draw_arrow(ax, 11, 7.1, 11, 5.6)
    draw_arrow(ax, 8.5, 7.1, 8.8, 5.6)

    # ── Management ──
    draw_rounded_box(ax, 6, 3.5, 6, 1.2, "#3cb44b",
                     "Population Management: Elitism + Replacement + Diversity Injection", fs=9)

    draw_arrow(ax, 9.8, 4.4, 7.5, 4.1)

    # Loop back
    ax.annotate("Iterate for\nN generations", xy=(3.0, 7.5),
                xytext=(3.0, 4.1),
                arrowprops=dict(arrowstyle="->", color="#888888", lw=2,
                                connectionstyle="arc3,rad=-0.4"),
                fontsize=9, color="#888888", ha="center")

    # ── Output ──
    draw_rounded_box(ax, 6, 1.8, 6, 1.2, "#000000",
                     "OUTPUT: Best Vehicle Routes (Min Total Distance, Feasible)", fs=9)
    draw_arrow(ax, 6, 3.0, 6, 2.4)

    # ── Legend ──
    legend_elements = [
        mpatches.Patch(color="#4363d8", label="Global Search (GA)"),
        mpatches.Patch(color="#e6194b", label="Local Refinement (LS)"),
        mpatches.Patch(color="#f58231", label="Encoding/Decoding"),
        mpatches.Patch(color="#3cb44b", label="Population Mgmt"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=8, framealpha=0.9)

    plt.savefig("../diagrams/diagram_architecture.png", dpi=150, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("  [OK] diagram_architecture.png")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Generating diagrams...")
    diagram_flowchart()
    diagram_encoding()
    diagram_local_search()
    diagram_architecture()
    print("All diagrams generated successfully!")
