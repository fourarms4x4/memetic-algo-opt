"""
Memetic Algorithm for the Traveling Salesman Problem (TSP)
===========================================================
A memetic algorithm combines a Genetic Algorithm (global search) with
Local Search (refinement) to solve optimization problems.

For TSP: find the shortest possible route that visits each city exactly
once and returns to the origin city.

Algorithm components:
  1. Population initialization (random permutations)
  2. Fitness evaluation (route distance)
  3. Selection (tournament selection)
  4. Crossover (Order Crossover - OX)
  5. Mutation (swap mutation)
  6. Local Search (2-opt heuristic)  <-- the "memetic" part
  7. Elitism (preserve best solutions)

The 2-opt local search improves each offspring by reversing subtour
segments to eliminate crossings, mimicking cultural/memetic evolution.
"""

import random
import math
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle

# ── Reproducibility ──────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ── Configuration ────────────────────────────────────────────────────────────
NUM_CITIES = 30
POP_SIZE   = 100
GENERATIONS = 200
TOURNAMENT_SIZE = 5
CROSSOVER_RATE  = 0.85
MUTATION_RATE   = 0.15
ELITISM_COUNT   = 2
LOCAL_SEARCH_DEPTH = 20   # how many 2-opt swaps to try per individual


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PROBLEM REPRESENTATION
# ═══════════════════════════════════════════════════════════════════════════════

def generate_cities(n, width=100, height=100):
    """Generate n random cities with (x, y) coordinates."""
    return np.column_stack((
        np.random.rand(n) * width,
        np.random.rand(n) * height
    ))


def distance_matrix(cities):
    """Precompute Euclidean distance matrix."""
    diff = cities[:, np.newaxis, :] - cities[np.newaxis, :, :]
    return np.sqrt((diff ** 2).sum(axis=2))


def tour_length(tour, dist_matrix):
    """Compute total length of a tour (returns to start)."""
    n = len(tour)
    return sum(dist_matrix[tour[i], tour[(i + 1) % n]] for i in range(n))


# ═══════════════════════════════════════════════════════════════════════════════
# 2. GENETIC OPERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def init_population(pop_size, n_cities):
    """Create a population of random tours (permutations)."""
    return [random.sample(range(n_cities), n_cities) for _ in range(pop_size)]


def tournament_select(population, fitnesses, k=TOURNAMENT_SIZE):
    """Select one parent via tournament selection."""
    contenders = random.sample(range(len(population)), k)
    best = min(contenders, key=lambda i: fitnesses[i])
    return population[best][:]


def order_crossover(parent1, parent2):
    """
    Order Crossover (OX):
    1. Pick a random slice from parent1.
    2. Copy that slice to the child.
    3. Fill remaining positions with genes from parent2 in order,
       skipping those already present.
    """
    n = len(parent1)
    a, b = sorted(random.sample(range(n), 2))

    child = [None] * n
    child[a:b] = parent1[a:b]

    # Fill from parent2, preserving relative order
    fill_pos = b % n
    for gene in parent2[b:] + parent2[:b]:
        if gene not in child:
            child[fill_pos] = gene
            fill_pos = (fill_pos + 1) % n

    return child


def swap_mutation(tour):
    """Swap two random cities in the tour."""
    a, b = random.sample(range(len(tour)), 2)
    tour[a], tour[b] = tour[b], tour[a]
    return tour


# ═══════════════════════════════════════════════════════════════════════════════
# 3. LOCAL SEARCH  —  the "memetic" component
# ═══════════════════════════════════════════════════════════════════════════════

def two_opt(tour, dist_matrix, max_iter=LOCAL_SEARCH_DEPTH):
    """
    2-opt local search: repeatedly reverse subtour segments to remove
    crossings. Stops when no improvement is found or max_iter reached.
    """
    n = len(tour)
    improved = True
    iterations = 0

    while improved and iterations < max_iter:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                # Compute delta: reversing (i+1 .. j) changes the tour
                a, b = tour[i], tour[(i + 1) % n]
                c, d = tour[j], tour[(j + 1) % n]

                old_cost = dist_matrix[a, b] + dist_matrix[c, d]
                new_cost = dist_matrix[a, c] + dist_matrix[b, d]

                if new_cost < old_cost:
                    # Reverse the segment
                    tour[i + 1 : j + 1] = reversed(tour[i + 1 : j + 1])
                    improved = True
            if improved:
                break
        iterations += 1

    return tour


def local_search_offspring(offspring, dist_matrix):
    """Apply 2-opt to each offspring (with probability ~ intensity)."""
    return [two_opt(ind[:], dist_matrix) for ind in offspring]


# ═══════════════════════════════════════════════════════════════════════════════
# 4. MEMETIC ALGORITHM MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════════

def memetic_algorithm(cities, dist_matrix, pop_size=POP_SIZE,
                      generations=GENERATIONS, crossover_rate=CROSSOVER_RATE,
                      mutation_rate=MUTATION_RATE, elitism=ELITISM_COUNT):
    """Run the memetic algorithm and return history of best fitnesses & tours."""

    n = len(cities)
    population = init_population(pop_size, n)

    history = {
        "best_fitness": [],
        "avg_fitness": [],
        "best_tour": [],
        "generation_markers": [],
    }

    for gen in range(generations):
        fitnesses = [tour_length(t, dist_matrix) for t in population]

        # Sort by fitness
        sorted_indices = np.argsort(fitnesses)
        sorted_pop = [population[i] for i in sorted_indices]
        sorted_fit = sorted(fitnesses)

        # Record history
        history["best_fitness"].append(sorted_fit[0])
        history["avg_fitness"].append(sum(fitnesses) / len(fitnesses))
        history["best_tour"].append(sorted_pop[0][:])
        history["generation_markers"].append(gen)

        # ── Elitism: keep best individuals ──
        new_pop = [sorted_pop[i][:] for i in range(elitism)]

        # ── Generate offspring ──
        while len(new_pop) < pop_size:
            p1 = tournament_select(population, fitnesses)
            p2 = tournament_select(population, fitnesses)

            if random.random() < crossover_rate:
                child1 = order_crossover(p1, p2)
                child2 = order_crossover(p2, p1)
            else:
                child1, child2 = p1[:], p2[:]

            if random.random() < mutation_rate:
                child1 = swap_mutation(child1)
            if random.random() < mutation_rate:
                child2 = swap_mutation(child2)

            new_pop.append(child1)
            if len(new_pop) < pop_size:
                new_pop.append(child2)

        # ── Memetic step: apply 2-opt local search to half the offspring ──
        # (Local search is expensive; apply to a subset each generation)
        search_count = max(1, pop_size // 4)
        for idx in random.sample(range(elitism, len(new_pop)),
                                 min(search_count, len(new_pop) - elitism)):
            new_pop[idx] = two_opt(new_pop[idx], dist_matrix)

        population = new_pop

        if gen % 20 == 0 or gen == generations - 1:
            print(f"Gen {gen:4d} | Best: {sorted_fit[0]:.2f}  "
                  f"Avg: {sorted_fit[len(sorted_fit)//2]:.2f}")

    return history


# ═══════════════════════════════════════════════════════════════════════════════
# 5. VISUALIZATION & ANIMATION
# ═══════════════════════════════════════════════════════════════════════════════

def plot_final_solution(cities, best_tour, dist_matrix, title="Memetic Algorithm — Final TSP Solution"):
    """Static plot of the best tour."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # ── Tour plot ──
    ordered = best_tour + [best_tour[0]]
    xs = cities[ordered, 0]
    ys = cities[ordered, 1]

    ax1.plot(xs, ys, "b-", linewidth=1.5, alpha=0.8, label="Tour")
    ax1.scatter(cities[:, 0], cities[:, 1], c="red", s=60, zorder=5, edgecolors="darkred")
    ax1.scatter(*cities[best_tour[0]], c="lime", s=120, zorder=6, edgecolors="green", label="Start")
    ax1.set_title("Best Tour Found")
    ax1.set_xlabel("X")
    ax1.set_ylabel("Y")
    ax1.legend()
    ax1.set_aspect("equal")

    distance = tour_length(best_tour, dist_matrix)
    ax1.text(0.02, 0.98, f"Distance: {distance:.2f}",
             transform=ax1.transAxes, fontsize=12, verticalalignment="top",
             bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))

    # ── Convergence plot ──
    ax2.plot(history["best_fitness"], "b-", linewidth=1.5, label="Best Fitness")
    ax2.plot(history["avg_fitness"], "orange", linewidth=1, alpha=0.6, label="Avg Fitness")
    ax2.set_title("Convergence Curve")
    ax2.set_xlabel("Generation")
    ax2.set_ylabel("Tour Distance")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.suptitle(title, fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("../outputs/memetic_tsp_final.png", dpi=150, bbox_inches="tight")
    plt.show()


def create_animation(cities, history, dist_matrix, output_file="../outputs/memetic_tsp_evolution.gif"):
    """
    Create an animated GIF showing:
      - Left: the best tour evolving over generations
      - Right: the convergence curve growing
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Memetic Algorithm — Evolution of TSP Solution", fontsize=14, fontweight="bold")

    n_cities = len(cities)

    # Tour plot
    scatter = ax1.scatter(cities[:, 0], cities[:, 1], c="red", s=60, zorder=5, edgecolors="darkred")
    start_marker = ax1.scatter(*cities[0], c="lime", s=120, zorder=6, edgecolors="green")
    line, = ax1.plot([], [], "b-", linewidth=1.5, alpha=0.8)
    dist_text = ax1.text(0.02, 0.98, "", transform=ax1.transAxes, fontsize=11,
                          verticalalignment="top",
                          bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))
    ax1.set_title("Best Tour")
    ax1.set_xlabel("X")
    ax1.set_ylabel("Y")
    ax1.set_aspect("equal")
    ax1.set_xlim(min(cities[:,0]) - 5, max(cities[:,0]) + 5)
    ax1.set_ylim(min(cities[:,1]) - 5, max(cities[:,1]) + 5)

    # Convergence plot
    best_line, = ax2.plot([], [], "b-", linewidth=1.5, label="Best Fitness")
    avg_line,  = ax2.plot([], [], "orange", linewidth=1, alpha=0.6, label="Avg Fitness")
    ax2.set_title("Convergence")
    ax2.set_xlabel("Generation")
    ax2.set_ylabel("Tour Distance")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, len(history["best_fitness"]))
    ax2.set_ylim(min(history["best_fitness"]) * 0.99, max(history["avg_fitness"]) * 1.02)

    # Sample frames (not every generation, to keep animation smooth & short)
    frame_step = max(1, len(history["best_fitness"]) // 100)

    def init():
        line.set_data([], [])
        best_line.set_data([], [])
        avg_line.set_data([], [])
        dist_text.set_text("")
        return line, best_line, avg_line, dist_text

    def update(frame_idx):
        gen = frame_idx * frame_step
        if gen >= len(history["best_fitness"]):
            gen = len(history["best_fitness"]) - 1

        tour = history["best_tour"][gen] + [history["best_tour"][gen][0]]
        xs = cities[tour, 0]
        ys = cities[tour, 1]
        line.set_data(xs, ys)
        dist_text.set_text(f"Gen {gen}  |  Dist: {history['best_fitness'][gen]:.2f}")

        x_vals = list(range(gen + 1))
        best_line.set_data(x_vals, history["best_fitness"][:gen + 1])
        avg_line.set_data(x_vals, history["avg_fitness"][:gen + 1])

        return line, best_line, avg_line, dist_text

    num_frames = len(history["best_fitness"]) // frame_step
    ani = animation.FuncAnimation(fig, update, frames=num_frames,
                                  init_func=init, interval=80, blit=True)

    plt.tight_layout()
    ani.save(output_file, writer="pillow", fps=12, dpi=100)
    print(f"\nAnimation saved to: {output_file}")
    plt.show()
    return ani


def detailed_report(cities, best_tour, dist_matrix, history, elapsed_time):
    """Print a structured report of the results."""
    print("\n" + "=" * 60)
    print("          MEMETIC ALGORITHM — TSP RESULTS                ")
    print("=" * 60)
    print(f"  Cities:                  {len(cities)}")
    print(f"  Population size:         {POP_SIZE}")
    print(f"  Generations:             {GENERATIONS}")
    print(f"  Crossover rate:          {CROSSOVER_RATE}")
    print(f"  Mutation rate:           {MUTATION_RATE}")
    print(f"  Local search (2-opt):    {LOCAL_SEARCH_DEPTH} iterations/individual")
    print("-" * 60)
    print(f"  Initial best distance:   {history['best_fitness'][0]:.2f}")
    print(f"  Final best distance:     {history['best_fitness'][-1]:.2f}")
    print(f"  Improvement:             {100 * (1 - history['best_fitness'][-1] / history['best_fitness'][0]):.1f}%")
    print(f"  Total computation time:  {elapsed_time:.2f} sec")
    print("=" * 60)

    # Convergence stats
    initial = history["best_fitness"][0]
    final = history["best_fitness"][-1]
    print(f"\nConvergence: {initial:.1f} → {final:.1f}")
    print("  The 2-opt local search helps the GA escape local minima,")
    print("  combining global exploration with local exploitation.")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. RUN EVERYTHING
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Generating cities ...")
    cities = generate_cities(NUM_CITIES)
    dist_matrix = distance_matrix(cities)

    print("Running Memetic Algorithm ...\n")
    start = time.time()
    history = memetic_algorithm(cities, dist_matrix)
    elapsed_time = time.time() - start

    best_tour = history["best_tour"][-1]

    detailed_report(cities, best_tour, dist_matrix, history, elapsed_time)

    print("\nPlotting final solution ...")
    plot_final_solution(cities, best_tour, dist_matrix)

    print("\nCreating evolution animation ...")
    create_animation(cities, history, dist_matrix)

    print("\nDone!")
