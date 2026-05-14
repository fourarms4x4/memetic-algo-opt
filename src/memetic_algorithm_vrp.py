"""
Memetic Algorithm for the Capacitated Vehicle Routing Problem (CVRP)
=====================================================================
A memetic algorithm combines a Genetic Algorithm (global search) with
Local Search operators (refinement) to solve the VRP.

CVRP definition:
  - 1 depot where all vehicles start and end
  - N customers, each with a location (x,y) and demand d_i
  - K vehicles, each with capacity Q
  - Each customer must be visited exactly once
  - Total demand per route ≤ Q
  - Objective: minimize total travel distance across all routes

Memetic components:
  ┌──────────────────────┐
  │  Genetic Algorithm   │  ← Global exploration
  │  (crossover +        │
  │   mutation)          │
  └──────────┬───────────┘
             │ offspring
             ▼
  ┌──────────────────────┐
  │  Local Search        │  ← Memetic refinement
  │  Intra-route:        │
  │    • 2-opt           │     Reverses subtours
  │    • Or-opt          │     Relocates segments
  │  Inter-route:        │
  │    • Relocate        │     Moves customer between routes
  │    • Exchange        │     Swaps two customers
  │    • 2-opt*          │     Crosses two routes
  └──────────────────────┘

Encoding: Giant Tour (permutation of customers) decoded via Prins' split.
Reference: Prins, C. (2004). "A simple and effective evolutionary algorithm
           for the vehicle routing problem."
"""

import random
import math
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ── Reproducibility ──────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ── VRP Configuration ────────────────────────────────────────────────────────
NUM_CUSTOMERS = 35
NUM_VEHICLES  = 5
VEHICLE_CAPACITY = 80
DEPOT_POS = (50, 50)         # depot at centre
MAP_SIZE  = 100

# ── MA Configuration ─────────────────────────────────────────────────────────
POP_SIZE         = 60
GENERATIONS      = 150
TOURNAMENT_SIZE  = 3
CROSSOVER_RATE   = 0.85
MUTATION_RATE    = 0.15
ELITISM_COUNT    = 2
LS_INTENSITY_POP = 0.15  # fraction of population that undergoes full LS each gen


# ═══════════════════════════════════════════════════════════════════════════════
# 1.  VRP INSTANCE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class VRPInstance:
    """Holds all problem data for a CVRP instance."""

    def __init__(self, depot, customers, demands, capacity, n_vehicles):
        self.depot = np.array(depot, dtype=float)
        self.customers = np.array(customers, dtype=float)
        self.demands = np.array(demands, dtype=float)
        self.capacity = capacity
        self.n_vehicles = n_vehicles
        self.n_customers = len(customers)

        self.points = np.vstack([self.depot.reshape(1, 2), self.customers])
        self._precompute_distances()

    def _precompute_distances(self):
        diff = self.points[:, np.newaxis, :] - self.points[np.newaxis, :, :]
        self.dist = np.sqrt((diff ** 2).sum(axis=2))

    def route_distance(self, route):
        """Distance of a single route: depot → ... → depot."""
        if len(route) == 0:
            return 0.0
        d = self.dist[0, route[0]]
        for i in range(len(route) - 1):
            d += self.dist[route[i], route[i + 1]]
        d += self.dist[route[-1], 0]
        return d

    def route_demand(self, route):
        return sum(self.demands[c - 1] for c in route)

    def is_route_feasible(self, route):
        return self.route_demand(route) <= self.capacity


def generate_vrp_instance(n_customers=NUM_CUSTOMERS,
                          n_vehicles=NUM_VEHICLES,
                          capacity=VEHICLE_CAPACITY,
                          depot=DEPOT_POS,
                          map_size=MAP_SIZE):
    """Generate a random CVRP instance."""
    # Cluster customers in random zones to make it non-trivial
    customers = []
    demands = []

    n_clusters = random.randint(3, 6)
    cluster_centers = np.random.rand(n_clusters, 2) * map_size * 0.8 + map_size * 0.1
    cluster_radii = [random.uniform(8, 20) for _ in range(n_clusters)]

    # Also add some scattered customers
    n_clustered = int(n_customers * 0.75)
    n_scattered = n_customers - n_clustered

    for i in range(n_clustered):
        c = random.randint(0, n_clusters - 1)
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, cluster_radii[c])
        x = cluster_centers[c][0] + r * math.cos(angle)
        y = cluster_centers[c][1] + r * math.sin(angle)
        customers.append([max(2, min(map_size - 2, x)),
                          max(2, min(map_size - 2, y))])
        demands.append(random.randint(3, 20))

    for i in range(n_scattered):
        customers.append([random.uniform(5, map_size - 5),
                          random.uniform(5, map_size - 5)])
        demands.append(random.randint(3, 20))

    # Ensure total demand fits an average loading of ~70%
    total_demand = sum(demands)
    target_load = 0.70
    needed_capacity = total_demand / (n_vehicles * target_load)
    adjusted_capacity = max(needed_capacity, capacity) if needed_capacity > capacity else capacity

    return VRPInstance(depot, customers, demands,
                       capacity=adjusted_capacity,
                       n_vehicles=n_vehicles)


# ═══════════════════════════════════════════════════════════════════════════════
# 2.  PRINS' SPLIT ALGORITHM  (decoding giant tour → feasible routes)
# ═══════════════════════════════════════════════════════════════════════════════

def prins_split(giant_tour, instance: VRPInstance, dist_matrix=None):
    """
    Prins' split algorithm (2004).

    Given a giant tour (permutation of all customers indexed from 1 to n),
    partition it optimally into feasible routes.

    Returns: (routes, total_distance)
      routes: list of lists, each inner list is a route (customer indices)
    """
    if dist_matrix is None:
        dist_matrix = instance.dist

    n = len(giant_tour)
    capacity = instance.capacity
    demands = instance.demands

    # V[i] = cumulative demand of first i customers in giant tour
    cum_demand = np.zeros(n + 1)
    for i in range(n):
        cum_demand[i + 1] = cum_demand[i] + demands[giant_tour[i] - 1]

    # DP: best[i] = min cost to serve first i customers
    best = np.full(n + 1, np.inf)
    pred = np.zeros(n + 1, dtype=int)   # predecessor in shortest path
    best[0] = 0.0

    for i in range(n):
        if best[i] >= np.inf:
            continue
        load = 0.0
        cost = dist_matrix[0, giant_tour[i]]   # depot → first customer
        for j in range(i, n):
            load += demands[giant_tour[j] - 1]
            if load > capacity:
                break
            # Add distance to next customer (or back to depot if last)
            if j > i:
                cost += dist_matrix[giant_tour[j - 1], giant_tour[j]]
            # Complete route: add return to depot
            route_cost = cost + dist_matrix[giant_tour[j], 0]
            if best[i] + route_cost < best[j + 1]:
                best[j + 1] = best[i] + route_cost
                pred[j + 1] = i

    # Reconstruct routes from pred
    routes = []
    pos = n
    while pos > 0:
        start = pred[pos]
        routes.append(giant_tour[start:pos])
        pos = start
    routes.reverse()

    return routes, best[n]


# ═══════════════════════════════════════════════════════════════════════════════
# 3.  FITNESS EVALUATION
# ═══════════════════════════════════════════════════════════════════════════════

def evaluate(giant_tour, instance: VRPInstance, penalty_factor=1000):
    """
    Evaluate a giant tour. Returns (total_distance, routes, feasible).
    Over-capacity routes incur a high penalty.
    """
    routes, total_dist = prins_split(giant_tour, instance)
    feasible = True
    penalty = 0.0

    for route in routes:
        overload = instance.route_demand(route) - instance.capacity
        if overload > 0:
            penalty += overload * penalty_factor
            feasible = False

    return total_dist + penalty, routes, feasible


# ═══════════════════════════════════════════════════════════════════════════════
# 4.  GENETIC OPERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def init_population(pop_size, n_customers):
    return [random.sample(range(1, n_customers + 1), n_customers)
            for _ in range(pop_size)]


def tournament_select(population, fitnesses, k=TOURNAMENT_SIZE):
    contenders = random.sample(range(len(population)), k)
    best = min(contenders, key=lambda i: fitnesses[i])
    return population[best][:]


def order_crossover(parent1, parent2):
    """Order Crossover (OX) for permutations."""
    n = len(parent1)
    a, b = sorted(random.sample(range(n), 2))
    child = [None] * n
    child[a:b] = parent1[a:b]
    fill_pos = b % n
    for gene in parent2[b:] + parent2[:b]:
        if gene not in child:
            child[fill_pos] = gene
            fill_pos = (fill_pos + 1) % n
    return child


def swap_mutation(tour):
    a, b = random.sample(range(len(tour)), 2)
    tour[a], tour[b] = tour[b], tour[a]
    return tour


def inversion_mutation(tour):
    """Reverse a random subsequence."""
    a, b = sorted(random.sample(range(len(tour)), 2))
    tour[a:b + 1] = reversed(tour[a:b + 1])
    return tour


def displacement_mutation(tour):
    """Move a random subsequence to a new position."""
    n = len(tour)
    a, b = sorted(random.sample(range(n), 2))
    segment = tour[a:b + 1]
    remainder = tour[:a] + tour[b + 1:]
    insert_pos = random.randint(0, len(remainder))
    new_tour = remainder[:insert_pos] + segment + remainder[insert_pos:]
    return new_tour


# ═══════════════════════════════════════════════════════════════════════════════
# 5.  LOCAL SEARCH OPERATORS  —  the memetic heart
# ═══════════════════════════════════════════════════════════════════════════════

# ── 5a. Intra-route operators ────────────────────────────────────────────────

def two_opt(route, dist):
    """2-opt: reverse segments within a single route. Returns improved route."""
    n = len(route)
    if n < 3:
        return route[:]
    best = route[:]
    improved = True
    while improved:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                a, b = best[i], best[(i + 1) % n]
                c, d = best[j], best[(j + 1) % n]
                if dist[a, b] + dist[c, d] > dist[a, c] + dist[b, d]:
                    best[i + 1:j + 1] = reversed(best[i + 1:j + 1])
                    improved = True
            if improved:
                break
    return best


def or_opt(route, dist, seg_len=3):
    """
    Or-opt: relocate a segment of given length to a better position.
    Uses delta evaluation for speed.
    """
    n = len(route)
    if n <= seg_len + 1:
        return route[:]
    best = route[:]
    improved = True
    while improved:
        improved = False
        for i in range(n - 1):  # start of segment
            for seg_l in [seg_len, 2, 1]:
                if i + seg_l > n:
                    continue
                seg = best[i:i + seg_l]
                remaining = best[:i] + best[i + seg_l:]
                # Edges around the segment being removed
                a = best[i - 1] if i > 0 else 0          # before segment
                b = best[i]                                # first of segment
                c = best[i + seg_l - 1]                    # last of segment
                d = best[i + seg_l] if i + seg_l < n else 0  # after segment

                old_contribution = dist[a, b] + dist[c, d]
                new_edge_without = dist[a, d] if a != 0 or d != 0 else (
                    dist[0, best[0]] + dist[best[-1], 0])  # approximating

                for p in range(len(remaining) + 1):
                    if p == i:
                        continue
                    y = remaining[p - 1] if p > 0 else 0       # before insertion
                    z = remaining[p] if p < len(remaining) else 0  # after insertion

                    # Delta: removing seg from old pos + inserting at new pos
                    delta = (dist[y, b] + dist[c, z] - dist[y, z]
                             + dist[a, d] - dist[a, b] - dist[c, d])
                    if delta < -1e-9:
                        cand = remaining[:p] + seg + remaining[p:]
                        best = cand
                        improved = True
                        break
                if improved:
                    break
            if improved:
                break
        n = len(best)
    return best


def compute_route_cost(route, dist):
    if len(route) == 0:
        return 0.0
    c = dist[0, route[0]]
    for i in range(len(route) - 1):
        c += dist[route[i], route[i + 1]]
    c += dist[route[-1], 0]
    return c


def intra_route_ls(routes, dist):
    """Apply 2-opt + Or-opt to each route."""
    return [or_opt(two_opt(r[:], dist), dist) for r in routes]


# ── 5b. Inter-route operators ────────────────────────────────────────────────

def relocate(routes, instance: VRPInstance):
    """
    Try moving one customer from one route to another.
    Uses delta evaluation for speed. First-accept strategy.
    """
    dist = instance.dist
    cap = instance.capacity
    dem = instance.demands
    best_routes = [r[:] for r in routes]

    # Precompute route costs and demands for delta evaluation
    route_costs = [compute_route_cost(r, dist) for r in best_routes]
    route_demands = [sum(dem[c - 1] for c in r) for r in best_routes]
    best_total = sum(route_costs)

    improved = True
    while improved:
        improved = False
        n = len(best_routes)
        for r1_idx in range(n):
            r1 = best_routes[r1_idx]
            if len(r1) == 0:
                continue
            for c_pos, c in enumerate(r1):
                c_demand = dem[c - 1]
                # Predecessor & successor in the route
                prev = r1[c_pos - 1] if c_pos > 0 else 0      # 0 = depot
                nxt = r1[(c_pos + 1) % len(r1)] if c_pos + 1 < len(r1) else 0
                # Cost of removing c from r1
                old_r1_delta = dist[prev, nxt] - dist[prev, c] - dist[c, nxt]

                for r2_idx in range(n):
                    if r1_idx == r2_idx:
                        continue
                    if route_demands[r2_idx] + c_demand > cap:
                        continue

                    r2 = best_routes[r2_idx]
                    for ins_pos in range(len(r2) + 1):
                        pin = r2[ins_pos - 1] if ins_pos > 0 else 0
                        nxt2 = r2[ins_pos] if ins_pos < len(r2) else 0
                        # Cost of inserting c into r2 at ins_pos
                        old_r2_delta = dist[pin, c] + dist[c, nxt2] - dist[pin, nxt2]

                        delta = old_r1_delta + old_r2_delta
                        if delta < -1e-9:
                            # Apply the move
                            best_routes[r1_idx] = r1[:c_pos] + r1[c_pos + 1:]
                            best_routes[r2_idx] = r2[:ins_pos] + [c] + r2[ins_pos:]
                            best_routes = [r[:] for r in best_routes if r]  # remove empty routes
                            best_total += delta
                            # Update cached values
                            route_costs = [compute_route_cost(r, dist) for r in best_routes]
                            route_demands = [sum(dem[cc - 1] for cc in r) for r in best_routes]
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    return best_routes


def exchange(routes, instance: VRPInstance):
    """
    Try swapping two customers between two different routes.
    Uses delta evaluation for speed. First-accept strategy.
    """
    dist = instance.dist
    cap = instance.capacity
    dem = instance.demands
    best_routes = [r[:] for r in routes]

    route_costs = [compute_route_cost(r, dist) for r in best_routes]
    route_demands = [sum(dem[c - 1] for c in r) for r in best_routes]
    best_total = sum(route_costs)

    improved = True
    while improved:
        improved = False
        n = len(best_routes)
        for r1_idx in range(n):
            r1 = best_routes[r1_idx]
            for c1_pos, c1 in enumerate(r1):
                d1 = dem[c1 - 1]
                prev1 = r1[c1_pos - 1] if c1_pos > 0 else 0
                nxt1 = r1[(c1_pos + 1) % len(r1)] if c1_pos + 1 < len(r1) else 0

                for r2_idx in range(r1_idx + 1, n):
                    r2 = best_routes[r2_idx]
                    for c2_pos, c2 in enumerate(r2):
                        d2 = dem[c2 - 1]

                        if route_demands[r1_idx] - d1 + d2 > cap:
                            continue
                        if route_demands[r2_idx] - d2 + d1 > cap:
                            continue

                        prev2 = r2[c2_pos - 1] if c2_pos > 0 else 0
                        nxt2 = r2[(c2_pos + 1) % len(r2)] if c2_pos + 1 < len(r2) else 0

                        # Delta: remove c1 from r1, insert c2; remove c2 from r2, insert c1
                        delta = (dist[prev1, c2] + dist[c2, nxt1] - dist[prev1, c1] - dist[c1, nxt1]
                                 + dist[prev2, c1] + dist[c1, nxt2] - dist[prev2, c2] - dist[c2, nxt2])

                        if delta < -1e-9:
                            new_r1 = r1[:]
                            new_r2 = r2[:]
                            new_r1[c1_pos] = c2
                            new_r2[c2_pos] = c1
                            best_routes[r1_idx] = new_r1
                            best_routes[r2_idx] = new_r2
                            best_total += delta
                            route_costs[r1_idx] = compute_route_cost(new_r1, dist)
                            route_costs[r2_idx] = compute_route_cost(new_r2, dist)
                            route_demands[r1_idx] = route_demands[r1_idx] - d1 + d2
                            route_demands[r2_idx] = route_demands[r2_idx] - d2 + d1
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    return best_routes


def two_opt_star(routes, instance: VRPInstance):
    """
    2-opt*: Cross two routes at a split point and reconnect.
    A → A[0:i] + B[j+1:]   and   B → B[0:j] + A[i+1:]
    Uses delta evaluation for speed.
    """
    dist = instance.dist
    cap = instance.capacity
    dem = instance.demands
    best_routes = [r[:] for r in routes]

    route_costs = [compute_route_cost(r, dist) for r in best_routes]
    route_demands = [sum(dem[c - 1] for c in r) for r in best_routes]
    best_total = sum(route_costs)

    improved = True
    while improved:
        improved = False
        n = len(best_routes)
        for r1_idx in range(n):
            r1 = best_routes[r1_idx]
            for i in range(-1, len(r1)):
                ai = r1[i] if i >= 0 else 0                      # node before split
                ai1 = r1[i + 1] if i + 1 < len(r1) else 0       # node after split
                dem_prefix_a = sum(dem[r1[k] - 1] for k in range(i + 1)) if i >= 0 else 0
                dem_suffix_a = route_demands[r1_idx] - dem_prefix_a

                for r2_idx in range(r1_idx + 1, n):
                    r2 = best_routes[r2_idx]
                    for j in range(-1, len(r2)):
                        bj = r2[j] if j >= 0 else 0
                        bj1 = r2[j + 1] if j + 1 < len(r2) else 0
                        dem_prefix_b = sum(dem[r2[k] - 1] for k in range(j + 1)) if j >= 0 else 0
                        dem_suffix_b = route_demands[r2_idx] - dem_prefix_b

                        # New routes: A_prefix + B_suffix, B_prefix + A_suffix
                        new_dem1 = dem_prefix_a + dem_suffix_b
                        new_dem2 = dem_prefix_b + dem_suffix_a
                        if new_dem1 > cap or new_dem2 > cap:
                            continue

                        # Delta = remove (ai,ai1) and (bj,bj1), add (ai,bj1) and (bj,ai1)
                        delta = (dist[ai, bj1] + dist[bj, ai1]
                                 - dist[ai, ai1] - dist[bj, bj1])

                        if delta < -1e-9:
                            # Apply crossover
                            prefix_a = r1[:i + 1] if i >= 0 else []
                            suffix_a = r1[i + 1:] if i + 1 <= len(r1) - 1 else []
                            prefix_b = r2[:j + 1] if j >= 0 else []
                            suffix_b = r2[j + 1:] if j + 1 <= len(r2) - 1 else []

                            new_r1 = prefix_a + suffix_b
                            new_r2 = prefix_b + suffix_a

                            new_routes = []
                            for k in range(n):
                                if k == r1_idx:
                                    if new_r1:
                                        new_routes.append(new_r1)
                                elif k == r2_idx:
                                    if new_r2:
                                        new_routes.append(new_r2)
                                else:
                                    new_routes.append(best_routes[k][:])

                            best_routes = new_routes
                            best_total += delta
                            route_costs = [compute_route_cost(r, dist) for r in best_routes]
                            route_demands = [sum(dem[cc - 1] for cc in r) for r in best_routes]
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break
        n = len(best_routes)  # may have changed

    return best_routes


def full_local_search(giant_tour, instance: VRPInstance):
    """
    Apply the complete local search pipeline to a solution:
      1. Decode giant tour → routes
      2. Intra-route LS (2-opt + Or-opt) on each route
      3. Inter-route LS (Relocate → Exchange → 2-opt*)
      4. Rebuild giant tour from improved routes
    """
    routes, _ = prins_split(giant_tour, instance)

    if not routes:
        return giant_tour

    # Intra-route
    routes = intra_route_ls(routes, instance.dist)

    # Inter-route (cycle until no improvement)
    for _ in range(3):
        prev = sum(compute_route_cost(r, instance.dist) for r in routes)
        routes = relocate(routes, instance)
        routes = exchange(routes, instance)
        routes = two_opt_star(routes, instance)
        curr = sum(compute_route_cost(r, instance.dist) for r in routes)
        if abs(curr - prev) < 1e-9:
            break

    # Rebuild giant tour
    new_giant = []
    for r in routes:
        new_giant.extend(r)

    # If some customers lost due to empty route merging, re-add them
    full_set = set(range(1, instance.n_customers + 1))
    present = set(new_giant)
    missing = full_set - present
    new_giant.extend(missing)

    return new_giant


# ═══════════════════════════════════════════════════════════════════════════════
# 6.  MEMETIC ALGORITHM MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════════

def memetic_algorithm_vrp(instance: VRPInstance, pop_size=POP_SIZE,
                          generations=GENERATIONS, crossover_rate=CROSSOVER_RATE,
                          mutation_rate=MUTATION_RATE, elitism=ELITISM_COUNT):
    """
    Memetic Algorithm for CVRP.

    Each generation:
      1. Evaluate fitness
      2. Elitism: preserve best
      3. Selection → Crossover → Mutation
      4. Apply local search to a fraction of the population
      5. Replace worst with new offspring
    """
    n = instance.n_customers
    population = init_population(pop_size, n)

    # Evaluate initial population
    fitnesses = []
    routes_archive = []
    for tour in population:
        fit, routes, _ = evaluate(tour, instance)
        fitnesses.append(fit)
        routes_archive.append(routes)

    history = {
        "best_fitness": [],
        "avg_fitness": [],
        "best_routes": [],
        "best_giant": [],
        "n_routes_history": [],
    }

    best_ever = float("inf")
    best_routes_ever = None
    best_giant_ever = None
    stagnation_counter = 0

    for gen in range(generations):
        # Record
        sorted_idx = np.argsort(fitnesses)
        best_fit = fitnesses[sorted_idx[0]]
        avg_fit = sum(fitnesses) / len(fitnesses)
        history["best_fitness"].append(best_fit)
        history["avg_fitness"].append(avg_fit)
        history["best_routes"].append(routes_archive[sorted_idx[0]])
        history["best_giant"].append(population[sorted_idx[0]][:])
        history["n_routes_history"].append(len(routes_archive[sorted_idx[0]]))

        improved_this_gen = best_fit < best_ever - 1e-9
        if improved_this_gen:
            best_ever = best_fit
            best_routes_ever = routes_archive[sorted_idx[0]]
            best_giant_ever = population[sorted_idx[0]][:]

        # ── Elitism ──
        sorted_pop = [population[i] for i in sorted_idx]
        sorted_fit = [fitnesses[i] for i in sorted_idx]
        sorted_routes = [routes_archive[i] for i in sorted_idx]

        new_pop = [sorted_pop[i][:] for i in range(elitism)]
        new_fit = [sorted_fit[i] for i in range(elitism)]
        new_routes = [sorted_routes[i] for i in range(elitism)]

        # ── Generate offspring ──
        while len(new_pop) < pop_size:
            p1 = tournament_select(population, fitnesses)
            p2 = tournament_select(population, fitnesses)

            if random.random() < crossover_rate:
                child = order_crossover(p1, p2)
            else:
                child = p1[:]

            r = random.random()
            if r < mutation_rate:
                child = swap_mutation(child)
            elif r < mutation_rate + 0.05:
                child = inversion_mutation(child)

            new_pop.append(child)

        # ── Evaluate new population ──
        new_fitnesses = []
        new_routes_archive = []
        penalty_factor = 1000 + gen * 5  # increasing penalty over time

        for tour in new_pop:
            fit, routes, feasible = evaluate(tour, instance, penalty_factor)
            new_fitnesses.append(fit)
            new_routes_archive.append(routes)

        # ── Memetic step: local search on a fraction of population ──
        ls_count = max(1, int(pop_size * LS_INTENSITY_POP))
        ls_candidates = random.sample(range(elitism, pop_size),
                                      min(ls_count, pop_size - elitism))

        for idx in ls_candidates:
            improved_tour = full_local_search(new_pop[idx], instance)
            new_pop[idx] = improved_tour
            fit, routes, _ = evaluate(improved_tour, instance)
            new_fitnesses[idx] = fit
            new_routes_archive[idx] = routes

        population = new_pop
        fitnesses = new_fitnesses
        routes_archive = new_routes_archive

        # ── Diversity injection: if stagnation detected, replace worst ──
        if gen > 0 and not improved_this_gen:
            stagnation_counter += 1
        else:
            stagnation_counter = 0

        if stagnation_counter >= 25:
            n_inject = max(1, pop_size // 5)
            new_random = init_population(n_inject, instance.n_customers)
            # Replace worst individuals (skip elites)
            for k in range(elitism, pop_size):
                if k - elitism < n_inject:
                    population[k] = new_random[k - elitism]
                    fit, routes, _ = evaluate(population[k], instance)
                    fitnesses[k] = fit
                    routes_archive[k] = routes
            stagnation_counter = 0
            print(f"       [Gen {gen}: Diversity injection — {n_inject} random individuals added]")

        if gen % 30 == 0 or gen == generations - 1:
            n_r = len(new_routes_archive[0])
            print(f"Gen {gen:4d} | Best: {best_fit:8.2f}  "
                  f"Avg: {sum(new_fitnesses)/len(new_fitnesses):8.2f}  "
                  f"Routes: {n_r}")

    history["best_ever"] = best_ever
    history["best_routes_ever"] = best_routes_ever
    history["best_giant_ever"] = best_giant_ever
    return history


# ═══════════════════════════════════════════════════════════════════════════════
# 7.  VISUALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

ROUTE_COLORS = [
    "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
    "#911eb4", "#42d4f4", "#f032e6", "#bfef45", "#fabed4",
    "#469990", "#dcbeff", "#9a6324", "#fffac8", "#800000",
]


def plot_final_solution(instance: VRPInstance, routes, history, elapsed):
    """Comprehensive 3-panel dashboard."""
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.35)

    # ── Panel 1: Route Map (spans left column) ──
    ax_map = fig.add_subplot(gs[:, 0])
    _draw_route_map(ax_map, instance, routes)

    # ── Panel 2: Convergence ──
    ax_conv = fig.add_subplot(gs[0, 1])
    ax_conv.plot(history["best_fitness"], "b-", linewidth=1.5, label="Best")
    ax_conv.plot(history["avg_fitness"], "orange", linewidth=0.8, alpha=0.6, label="Avg")
    ax_conv.set_title("Convergence Curve")
    ax_conv.set_xlabel("Generation")
    ax_conv.set_ylabel("Total Distance")
    ax_conv.legend(fontsize=8)
    ax_conv.grid(True, alpha=0.3)

    # ── Panel 3: Number of routes ──
    ax_routes = fig.add_subplot(gs[0, 2])
    ax_routes.plot(history["n_routes_history"], "g-", linewidth=1.5)
    ax_routes.set_title("Number of Routes Over Time")
    ax_routes.set_xlabel("Generation")
    ax_routes.set_ylabel("Routes Used")
    ax_routes.grid(True, alpha=0.3)
    n_routes = len(routes)
    ax_routes.axhline(y=n_routes, color="r", linestyle="--", alpha=0.5,
                      label=f"Final: {n_routes}")
    ax_routes.legend(fontsize=8)

    # ── Panel 4: Route details table ──
    ax_table = fig.add_subplot(gs[1, 1:])
    _draw_route_table(ax_table, instance, routes)

    fig.suptitle("Memetic Algorithm — CVRP Solution Dashboard",
                 fontsize=15, fontweight="bold")
    plt.savefig("../outputs/memetic_vrp_final.png", dpi=150, bbox_inches="tight")
    plt.show()


def _draw_route_map(ax, instance, routes):
    """Draw the VRP route map with depot, customers, and routes."""
    customers = instance.customers
    depot = instance.depot
    dist = instance.dist
    dem = instance.demands

    # Depot
    ax.scatter(*depot, c="black", s=200, marker="s", zorder=10, label="Depot")
    ax.annotate("DEPOT", depot + [1.5, 2], fontsize=9, fontweight="bold",
                color="black", ha="center")

    # Customers: size proportional to demand
    sizes = np.maximum(20, (dem / instance.capacity) * 120)
    ax.scatter(customers[:, 0], customers[:, 1], c="gray", s=sizes,
               zorder=5, edgecolors="black", linewidth=0.5, alpha=0.4, label="Customers")

    total_dist = 0.0
    for idx, route in enumerate(routes):
        if not route:
            continue
        color = ROUTE_COLORS[idx % len(ROUTE_COLORS)]
        pts = np.vstack([depot, customers[[c - 1 for c in route]], depot])
        ax.plot(pts[:, 0], pts[:, 1], "-", color=color, linewidth=2, alpha=0.85)
        ax.scatter(customers[[c - 1 for c in route], 0],
                   customers[[c - 1 for c in route], 1],
                   c=color, s=40, zorder=6, edgecolors="black", linewidth=0.5)
        r_dist = instance.route_distance(route)
        r_dem = instance.route_demand(route)
        total_dist += r_dist

        # Label midpoint of route
        mid = len(route) // 2
        mid_pt = customers[route[mid] - 1] if route else depot
        ax.annotate(f"V{idx + 1}", mid_pt + [1, 2], fontsize=8,
                    color=color, fontweight="bold")

    ax.set_title(f"Vehicle Routes  |  {len(routes)} routes  |  Total: {total_dist:.1f}")
    ax.set_xlabel("X coordinate")
    ax.set_ylabel("Y coordinate")
    ax.set_xlim(-2, MAP_SIZE + 2)
    ax.set_ylim(-2, MAP_SIZE + 2)
    ax.set_aspect("equal")
    ax.legend(loc="upper right", fontsize=7)


def _draw_route_table(ax, instance, routes):
    """Display a table of route statistics."""
    ax.axis("off")
    dist = instance.dist

    col_labels = ["Vehicle", "# Stops", "Demand", "Capacity %", "Distance", "Route"]
    table_data = []
    total_dist = 0.0

    for idx, route in enumerate(routes):
        r_dist = instance.route_distance(route)
        r_dem = instance.route_demand(route)
        pct = 100 * r_dem / instance.capacity
        max_display = 8
        if len(route) > max_display:
            route_str = str(route[:max_display])[:-1] + ", ...]"
        else:
            route_str = str(route)
        total_dist += r_dist
        table_data.append([
            f"V{idx + 1}", len(route), f"{r_dem:.0f}",
            f"{pct:.0f}%", f"{r_dist:.1f}", route_str
        ])

    # Totals row
    total_dem = sum(instance.demands)
    table_data.append(["TOTAL", sum(len(r) for r in routes), f"{total_dem:.0f}",
                       f"{100 * total_dem / (len(routes) * instance.capacity):.0f}%",
                       f"{total_dist:.1f}", ""])

    table = ax.table(cellText=table_data, colLabels=col_labels,
                     cellLoc="center", loc="center",
                     colWidths=[0.08, 0.08, 0.08, 0.10, 0.10, 0.40])
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.0, 1.4)

    # Header style
    for j in range(len(col_labels)):
        table[0, j].set_facecolor("#40466e")
        table[0, j].set_text_props(color="white", fontweight="bold")

    # Alternating row colors
    for i in range(len(table_data)):
        color = "#f5f5f5" if i % 2 == 0 else "white"
        for j in range(len(col_labels)):
            table[i + 1, j].set_facecolor(color)

    # Highlight last row
    last = len(table_data)
    for j in range(len(col_labels)):
        table[last, j].set_facecolor("#e8e8e8")
        table[last, j].set_text_props(fontweight="bold")

    ax.set_title("Route Details", fontsize=12, fontweight="bold")


# ═══════════════════════════════════════════════════════════════════════════════
# 8.  ANIMATION
# ═══════════════════════════════════════════════════════════════════════════════

def create_animation(instance: VRPInstance, history,
                     output_file="../outputs/memetic_vrp_evolution.gif"):
    """Animate the evolution of VRP routes."""

    fig = plt.figure(figsize=(18, 9))
    gs = fig.add_gridspec(1, 3, wspace=0.3)

    ax_map = fig.add_subplot(gs[0, :2])
    ax_conv = fig.add_subplot(gs[0, 2])

    customers = instance.customers
    depot = instance.depot
    cap = instance.capacity
    dem = instance.demands

    # Route map setup
    sizes = np.maximum(20, (dem / cap) * 120)
    ax_map.scatter(customers[:, 0], customers[:, 1], c="gray", s=sizes,
                   zorder=5, edgecolors="black", linewidth=0.5, alpha=0.4)
    ax_map.scatter(*depot, c="black", s=200, marker="s", zorder=10)
    ax_map.set_title("Best Routes")
    ax_map.set_xlabel("X")
    ax_map.set_ylabel("Y")
    ax_map.set_xlim(-2, MAP_SIZE + 2)
    ax_map.set_ylim(-2, MAP_SIZE + 2)
    ax_map.set_aspect("equal")

    # Store lines for each route
    max_routes = len(history["best_routes"][0])
    route_lines = [ax_map.plot([], [], "-", linewidth=2)[0]
                   for _ in range(max_routes * 2)]  # extra buffer

    info_text = ax_map.text(0.02, 0.98, "", transform=ax_map.transAxes,
                            fontsize=10, verticalalignment="top",
                            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))

    # Convergence
    best_line, = ax_conv.plot([], [], "b-", linewidth=1.5, label="Best")
    avg_line, = ax_conv.plot([], [], "orange", linewidth=1, alpha=0.6, label="Avg")
    ax_conv.set_title("Convergence")
    ax_conv.set_xlabel("Generation")
    ax_conv.set_ylabel("Distance")
    ax_conv.legend(fontsize=8)
    ax_conv.grid(True, alpha=0.3)
    ax_conv.set_xlim(0, len(history["best_fitness"]))
    y_min = min(history["best_fitness"]) * 0.95
    y_max = max(history["avg_fitness"]) * 1.05
    ax_conv.set_ylim(y_min, y_max)

    frame_step = max(1, len(history["best_fitness"]) // 120)

    def init():
        for line in route_lines:
            line.set_data([], [])
        best_line.set_data([], [])
        avg_line.set_data([], [])
        info_text.set_text("")
        return route_lines + [best_line, avg_line, info_text]

    def update(frame_idx):
        gen = min(frame_idx * frame_step, len(history["best_fitness"]) - 1)
        routes = history["best_routes"][gen]

        for line in route_lines:
            line.set_data([], [])

        for idx, route in enumerate(routes):
            if not route or idx >= len(route_lines):
                continue
            color = ROUTE_COLORS[idx % len(ROUTE_COLORS)]
            pts = np.vstack([depot, customers[[c - 1 for c in route]], depot])
            route_lines[idx].set_data(pts[:, 0], pts[:, 1])
            route_lines[idx].set_color(color)

        total = instance.route_distance(routes[0]) if routes else 0
        for r in routes[1:]:
            total += instance.route_distance(r)

        info_text.set_text(f"Gen {gen:4d}\nRoutes: {len(routes)}"
                           f"\nDist: {history['best_fitness'][gen]:.1f}")

        x_vals = range(gen + 1)
        best_line.set_data(x_vals, history["best_fitness"][:gen + 1])
        avg_line.set_data(x_vals, history["avg_fitness"][:gen + 1])

        return route_lines + [best_line, avg_line, info_text]

    num_frames = len(history["best_fitness"]) // frame_step
    ani = animation.FuncAnimation(fig, update, frames=num_frames,
                                  init_func=init, interval=100,
                                  blit=True, repeat=False)

    fig.suptitle("Memetic Algorithm — VRP Evolution", fontsize=14, fontweight="bold")
    ani.save(output_file, writer="pillow", fps=10, dpi=100)
    print(f"\nAnimation saved to: {output_file}")
    plt.show()
    return ani


# ═══════════════════════════════════════════════════════════════════════════════
# 9.  REPORT
# ═══════════════════════════════════════════════════════════════════════════════

def detailed_report(instance: VRPInstance, routes, history, elapsed):
    print("\n" + "=" * 70)
    print("       MEMETIC ALGORITHM — CVRP RESULTS")
    print("=" * 70)
    print(f"  Problem scale:")
    print(f"    Customers:             {instance.n_customers}")
    print(f"    Vehicles available:    {instance.n_vehicles}")
    print(f"    Vehicle capacity:      {instance.capacity:.1f}")
    print(f"    Total demand:          {sum(instance.demands):.1f}")
    print(f"    Demand/Capacity (avg): {100 * sum(instance.demands) / (instance.n_vehicles * instance.capacity):.1f}%")
    print(f"  Algorithm parameters:")
    print(f"    Population size:       {POP_SIZE}")
    print(f"    Generations:           {GENERATIONS}")
    print(f"    Crossover rate:        {CROSSOVER_RATE}")
    print(f"    Mutation rate:         {MUTATION_RATE}")
    print(f"    Local search intensity:{LS_INTENSITY_POP * 100:.0f}% of pop")
    print("-" * 70)
    print(f"  Results:")
    print(f"    Initial best:          {history['best_fitness'][0]:.2f}")
    print(f"    Final best:            {history['best_fitness'][-1]:.2f}")
    print(f"    Improvement:           {100 * (1 - history['best_fitness'][-1] / max(1, history['best_fitness'][0])):.1f}%")
    print(f"    Routes used:           {len(routes)}")
    print(f"    Computation time:      {elapsed:.2f} sec")
    print("=" * 70)

    print("\nRoute breakdown:")
    print(f"  {'Vehicle':<9} {'Stops':<7} {'Demand':<9} {'Capacity %':<11} {'Distance':<10}")
    print("  " + "-" * 46)
    total_d = 0.0
    for i, r in enumerate(routes):
        d = instance.route_distance(r)
        dem_r = instance.route_demand(r)
        pct = 100 * dem_r / instance.capacity
        total_d += d
        print(f"  V{i+1:<8} {len(r):<7} {dem_r:<9.1f} {pct:<11.1f} {d:<10.1f}")
    print("  " + "-" * 46)
    print(f"  {'TOTAL':<9} {sum(len(r) for r in routes):<7} "
          f"{sum(instance.demands):<9.1f} {'':<11} {total_d:<10.1f}")

    violated = any(instance.route_demand(r) > instance.capacity + 1e-9 for r in routes)
    print(f"\n  All capacity constraints satisfied: {'Yes' if not violated else 'NO!'}")


# ═══════════════════════════════════════════════════════════════════════════════
# 10.  MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("╔" + "═" * 56 + "╗")
    print("║" + "  MEMETIC ALGORITHM FOR VEHICLE ROUTING PROBLEM (CVRP)".center(56) + "║")
    print("║" + "  GA + Local Search = Memetic Algorithm".center(56) + "║")
    print("╚" + "═" * 56 + "╝\n")

    print("Generating VRP instance ...")
    instance = generate_vrp_instance()

    print(f"  Customers: {instance.n_customers}  |  "
          f"Vehicles: {instance.n_vehicles}  |  "
          f"Capacity: {instance.capacity:.1f}\n")

    print("Running Memetic Algorithm ...\n")
    start = time.time()
    history = memetic_algorithm_vrp(instance)
    elapsed = time.time() - start

    best_routes = history["best_routes_ever"]
    detailed_report(instance, best_routes, history, elapsed)

    print("\nPlotting final solution dashboard ...")
    plot_final_solution(instance, best_routes, history, elapsed)

    print("\nCreating evolution animation ...")
    create_animation(instance, history)

    print("\nAll done!")
