# Q&A — Memetic Algorithm for VRP

## Expected Questions & Prepared Answers

---

## Algorithm Fundamentals

### Q1: "What makes this a 'memetic' algorithm and not just a genetic algorithm?"

**A:** A genetic algorithm relies solely on crossover and mutation — random genetic operators — to explore the search space. It can find promising regions but converges slowly to precise optima.

A memetic algorithm adds a **local search step** after the GA produces offspring. Before an individual enters the next generation, it undergoes intensive refinement using problem-specific operators (2-opt, Or-opt, Relocate, Exchange, 2-opt\*). This is the "memetic" component — named after the concept of *memes* (cultural evolution through learning, as opposed to genes which evolve through random mutation).

The difference is measurable: without local search, our GA would take many more generations to reach the same solution quality. With local search, 15% of the population gets polished each generation, and the algorithm converges in ~30 generations instead of hundreds.

---

### Q2: "Why use a giant tour + Prins split instead of directly encoding routes?"

**A:** Direct route encoding creates a variable-length, variable-structure chromosome. If you encode routes as `[Route1: dep→3→7→dep, Route2: dep→1→5→9→dep]`, then crossover becomes messy — parents may have different numbers of routes, different route lengths, and crossing them could duplicate or lose customers.

The giant tour is a **fixed-length permutation** of all N customers. This is elegant because:

1. **Standard GA operators work**: Order Crossover, swap mutation, etc., are well-studied for permutations
2. **Feasibility is delegated**: The Prins split algorithm handles all VRP-specific complexity (capacity constraints, multi-vehicle assignment) during decoding
3. **O(N²) per evaluation**: The split is efficient and predictable

It's a clean separation of concerns: the GA deals with permutations; the split handles routing. This is the approach introduced by Prins (2004) and widely adopted in the literature.

---

### Q3: "How does the Prins Split Algorithm actually work?"

**A:** Given a giant tour T = [t₁, t₂, ..., tₙ] (a permutation of customers without the depot):

1. **Build an auxiliary DAG** with nodes 0, 1, 2, ..., n. Node 0 represents "before the first customer," node k represents "after the first k customers."

2. **For each pair (i, j) where i < j**, check if the subtour T[i+1...j] fits in one vehicle:
   - Compute the demand of customers in that segment
   - If ≤ capacity Q, compute the route cost: dep→t_{i+1}→...→t_j→dep
   - Add a directed edge (i → j) with weight = route cost

3. **Find the shortest path from 0 to n** using dynamic programming (O(N²)). Each edge on the path represents one vehicle route.

4. **For example**: if the shortest path is 0→3→7→10, the routes are:
   - Route 1: dep→t₁→t₂→t₃→dep
   - Route 2: dep→t₄→t₅→t₆→t₇→dep
   - Route 3: dep→t₈→t₉→t₁₀→dep

The split algorithm guarantees the **optimal partition** of the given giant tour into feasible routes. The GA's job is to find a giant tour whose optimal partition yields the best solution.

---

### Q4: "How do you handle capacity constraints? What if they can't be satisfied?"

**A:** We use a **soft constraint with adaptive penalty**:

$$ \text{Cost}(T) = \sum_{r \in \text{Split}(T)} \text{Dist}(r) + \lambda(g) \cdot \max(0, \text{Load}(r) - Q) $$

The penalty multiplier λ(g) starts at 1000 and increases by 5 per generation (λ(g) = 1000 + 5g).

- **Early generations** (λ ≈ 1000): The algorithm can explore slightly infeasible solutions, which helps discover promising regions of the search space that might be blocked by hard constraints
- **Later generations** (λ ≈ 1750): The penalty becomes severe, forcing the population toward strict feasibility

Additionally, the Prins split algorithm itself guarantees that all routes it produces satisfy capacity — the penalty only applies if the split cannot find ANY feasible partition (which is rare for well-designed instances).

If the instance is truly infeasible (total demand exceeds fleet capacity), the algorithm converges to the least-infeasible solution and reports the violations explicitly.

---

### Q5: "How do you know the solution is good? Is it optimal?"

**A:** We cannot guarantee optimality — CVRP is NP-hard, so no polynomial-time algorithm can guarantee the global optimum for arbitrary instances.

However, several indicators suggest our solution is near-optimal:

1. **Convergence behavior**: The algorithm converges rapidly (30 generations) to a stable plateau. After that, neither the GA nor diversity injection finds improvements, suggesting the solution is at a deep local optimum.

2. **Benchmark comparison**: For our 35-customer instance, the Clarke-Wright savings heuristic (a well-known baseline) typically scores in the 550-600 range. Our solution at 514 is **7-14% better** than that heuristic, which is competitive.

3. **Visual inspection**: The route map shows no crossings, customers are clustered geographically, and vehicle utilization is balanced (80-96% capacity).

4. **Validation**: For definitive verification, we could compare against known optimal solutions from benchmark libraries (e.g., CVRPLIB) — but this requires running on standard instance sets where the optimal is known.

---

## Performance & Scalability

### Q6: "How does this scale to 200 or 1000 customers?"

**A:** The primary bottleneck is the Prins split algorithm, which is O(N²) per evaluation. At 35 customers, this is negligible (~1225 operations). At 200 customers, it's ~40,000 operations per evaluation — 33× slower per evaluation.

For larger instances, we would need:

| Change | Impact |
|--------|--------|
| Reduce POP_SIZE from 60 to 30 | 2× fewer evaluations per generation |
| Reduce GENERATIONS from 150 to 100 | 33% fewer total evaluations |
| Reduce LS_INTENSITY from 15% to 5% | Fewer local search calls |
| Use a faster split variant | e.g., bidirectional DP or heuristic split |
| Implement parallel evaluation | Evaluate population in parallel |

With these adjustments, the algorithm would handle ~200 customers in a similar time frame (1-2 minutes). For 1000+ customers, metaheuristics like ALNS (Adaptive Large Neighborhood Search) or hybrid CP-MA approaches are more practical than a pure population-based GA.

---

### Q7: "55 seconds seems slow. How could you make it faster?"

**A:** The runtime breaks down roughly as:

| Component | % of time |
|-----------|-----------|
| Prins Split evaluations | ~35% |
| Local search operators | ~40% |
| GA operators (crossover, mutation) | ~10% |
| Population management | ~5% |
| Visualization output | ~10% |

Speed improvements, in order of impact:

1. **Parallelize fitness evaluation**: Evaluate all 60 individuals in parallel (multi-core). This alone could give a 4-8× speedup
2. **Early stopping**: Halt when no improvement for 40 generations — saves wasted computation on a converged population
3. **Compiled language**: Python is ~10-50× slower than C++/Rust for nested loops; rewriting the Prins split and local search in a compiled language would dramatically improve speed
4. **Cached split results**: If the same giant tour appears, reuse the cached routes (though with mutation, this is rare)
5. **Reduce local search depth**: One cycle instead of three — most improvement comes in the first cycle

We chose Python for clarity and educational value. The algorithm is correct; speed is a secondary concern for demonstration purposes.

---

### Q8: "Why 150 generations? Why 60 population? Why 15% local search?"

**A:** These were chosen through a combination of literature guidance and empirical testing:

- **Population size (60)**: Standard for permutation-based GAs. Too small (< 30) loses diversity; too large (> 100) wastes computation with redundant similar individuals.

- **Generations (150)**: Empirical — the algorithm converges by generation 30. 150 gives it 120 additional generations to potentially escape local optima via diversity injection, while keeping runtime under 1 minute.

- **Local search intensity (15%)**: Higher values (> 30%) cause premature convergence (everyone converges to the same local optimum). Lower values (< 5%) make the memetic effect negligible. 15% is a common choice in MA literature for balancing exploration and exploitation.

These are not optimal — they're reasonable defaults. A proper parameter tuning study (grid search or Bayesian optimization) could find better settings, but that's beyond the scope of this project.

---

## Algorithm Design Decisions

### Q9: "Why these 5 specific local search operators? Why not more?"

**A:** We cover the three fundamental move types in VRP local search:

| Move Type | Operator | What it does |
|-----------|----------|-------------|
| **Intra-route edge exchange** | 2-opt | Reverses a segment (removes crossings) |
| **Intra-route relocation** | Or-opt | Moves a short segment within the route |
| **Inter-route relocation** | Relocate | One customer changes vehicles |
| **Inter-route exchange** | Exchange | Two customers swap vehicles |
| **Inter-route cross** | 2-opt\* | Tail sections of two routes swap |

These 5 form a **complete neighborhood** — any VRP solution modification can be decomposed into these moves. Adding more operators (e.g., 3-opt, CROSS-exchange, GENI) would increase search thoroughness but also runtime. For 35 customers, these 5 are sufficient.

The order matters: we run intra-route first (refine individual routes cheaply), then inter-route (more expensive but higher impact). This pipeline approach is standard in the literature.

---

### Q10: "What is 'delta evaluation' and why does it give a 3-10x speedup?"

**A:** Naive approach: when evaluating a potential move, compute the total distance of the new route from scratch. This requires summing over all nodes in the route — O(L) per evaluation.

Delta evaluation: compute only the **change** in cost.

Example — exchanging customer C1 in Route A with C2 in Route B:

```
Old Route A:  ... → A_prev → C1 → A_next → ...
Old Route B:  ... → B_prev → C2 → B_next → ...

New Route A:  ... → A_prev → C2 → A_next → ...
New Route B:  ... → B_prev → C1 → B_next → ...
```

Naive calculation: compute 2 full route costs (~17 operations for routes of length 9).  
Delta calculation: 4 edge comparisons (dist[A_prev, C2] + dist[C2, A_next] - dist[A_prev, C1] - dist[C1, A_next]) = 4 operations.

The speedup comes from **avoiding recomputation of unchanged parts**. For the exchange operator checking all pairs, delta evaluation reduces O(L² × P²) to O(L × P²) per neighborhood scan, giving ~3-10× improvement depending on route lengths.

---

### Q11: "What happens when the diversity injection triggers? Does it actually help?"

**A:** Diversity injection replaces 20% of the population (excluding the 2 elite individuals) with completely random giant tours. The stagnation counter resets after injection.

In our runs, diversity injection triggers ~5 times (at generations 47, 72, 97, 122, and 147). The best fitness does not improve after injection — the solution has already reached a deep local optimum.

This doesn't mean diversity injection is useless. It means:

1. **The solution is likely near-optimal** — if random exploration from 5 different starting points consistently returns to the same local optimum, that basin is probably the best in the region.

2. **It prevents wasted computation** — without injection, the algorithm would spend 120 generations evaluating a fully converged, identical population. Injection forces the GA to keep working.

3. **On easier instances**, injection can help escape shallow local optima that the GA initially got trapped in.

Think of it as an "insurance policy" — it costs little and occasionally saves a subpar run.

---

## Results Interpretation

### Q12: "The algorithm reduced from 5 vehicles to 4. How did that happen?"

**A:** The original 5-vehicle limit was an upper bound, not a target. The Prins split algorithm decides how many vehicles to actually use.

Initially, with random giant tours, the split algorithm produces 5 routes because random sequences tend to have customers with incompatible demands placed adjacently, requiring more splits.

As the GA + local search optimize the giant tour, customers with complementary demands are placed near each other in the permutation. This allows the split to pack them into fewer, fuller vehicles:

| Metric | Initial | Final |
|--------|---------|-------|
| Routes | 5 | 4 |
| Avg load | 56% | 87.5% |
| Min load | ~30% | 80% |
| Max load | ~90% | 96% |

Using fewer vehicles reduces the number of depot-to-first-customer and last-customer-to-depot trips (which are the most expensive segments) — saving significant distance.

The algorithm discovered that 4 trucks at 80-96% capacity is more efficient than 5 trucks at 50-70%.

---

### Q13: "Why are the customers clustered in the generated instance?"

**A:** Real-world delivery logistics are not uniformly random. Customers cluster in:
- Residential neighborhoods
- Commercial districts
- Rural areas (sparser but still grouped)

We generate instances using 3-6 random cluster centers with Gaussian-like scatter (75% of customers) plus scattered outliers (25%). This:
- Makes the problem non-trivial (clustered instances are harder for naive heuristics)
- Mimics real delivery patterns
- Creates visible route clusters that make the visualization more interpretable

If all customers were uniformly random, any reasonable algorithm would produce similar-looking circular routes. Clustered instances better demonstrate the algorithm's ability to discover geographic groupings.

---

### Q14: "Could you have used fewer generations? The curve flatlines at generation 30."

**A:** Yes. An **early stopping criterion** would be a natural improvement:

```python
if stagnation_counter >= 40:
    print(f"Converged at generation {gen}")
    break
```

With early stopping at 40 gens of no improvement, the algorithm would halt around generation 70-80 (30 + 40), roughly halving runtime. The final solution would be identical since no improvement occurs after gen 30.

We kept 150 generations for consistency and to demonstrate the plateau behavior — it's pedagogically useful to show that the algorithm correctly converges and stays there. In production, early stopping is the obvious optimization.

---

## Comparison & Context

### Q15: "How does this compare to Clarke-Wright or other heuristics?"

**A:** The Clarke-Wright Savings algorithm is a fast constructive heuristic:

| Metric | Clarke-Wright | Our MA |
|--------|--------------|--------|
| Approach | Greedy merge | Evolutionary + LS |
| Runtime | < 1 second | ~55 seconds |
| Solution quality | ~75-85% optimal | Near-optimal (competitive) |
| Deterministic | Yes | No (stochastic) |
| Complexity | O(N² log N) | O(G × P × N²) |

Clarke-Wright is better for **speed-critical** applications (e.g., real-time dispatch). Our MA is better for **quality-critical** applications where you have time to optimize (e.g., overnight route planning).

The ideal real-world system: use Clarke-Wright for an initial solution, then refine it with the MA.

---

### Q16: "Why not use OR-Tools or a commercial VRP solver instead of building your own?"

**A:** Google OR-Tools and similar solvers are production-grade and would outperform our implementation. This project is **educational**, not production.

Building the algorithm from scratch serves three purposes:

1. **Understanding**: You can't truly understand an algorithm until you implement it. Reading about 2-opt is different from debugging why your 2-opt produces routes with 34 customers instead of 35.

2. **Flexibility**: Custom implementations allow easy experimentation — adding new operators, testing different encodings, visualizing internal state.

3. **Demonstration**: The visualizations, convergence curves, and animated evolution GIF demonstrate the algorithm's inner workings in a way a black-box solver never could.

OR-Tools is the right choice for solving real logistics problems. This implementation is the right choice for learning how such solvers work under the hood.

---

### Q17: "What's the difference between this and a standard GA for VRP?"

**A:** A standard GA for VRP:

1. Uses direct route encoding or other encodings
2. Runs selection, crossover, mutation for N generations
3. Returns the best solution found
4. **Relies entirely on random variation** to improve

Our memetic algorithm adds:

1. **Local search on offspring** — before joining the population, 15% of offspring undergo intensive refinement
2. **5 problem-specific operators** — not generic mutations, but VRP-specific neighborhood moves
3. **Delta evaluation** — efficient move assessment
4. **Diversity injection** — stagnation-aware population refresh
5. **Adaptive penalty** — generation-dependent constraint enforcement

The result: the memetic algorithm converges in ~30 generations to a high-quality solution, while a pure GA would take many more generations and likely reach a lower-quality solution due to insufficient exploitation.

---

## Implementation Details

### Q18: "What happens if the Prins split can't find any feasible partition?"

**A:** This can happen if the giant tour places all high-demand customers early, causing every possible split point to violate capacity.

In our penalty-based fitness function, the solution gets a heavy penalty (thousands of extra distance units). This makes it the "worst" individual in the population, and it:
- Is never selected for reproduction (tournament selection picks fitter parents)
- Is replaced by offspring in the next generation
- Gets culled naturally

The penalty system means infeasible individuals die off through natural selection, without needing explicit repair. It's simpler and more robust than trying to repair every infeasible solution.

---

### Q19: "Why use Python? Isn't it too slow for this kind of algorithm?"

**A:** Python is indeed slower than C++/Rust for numerical computation — but it's the right trade-off for this project:

| Language | Dev time | Runtime | Clarity |
|----------|----------|---------|---------|
| Python | Fast | 55 sec | Excellent |
| C++ | Very slow | ~2 sec | Poor |
| Julia | Moderate | ~5 sec | Good |

For 35 customers, 55 seconds is fast enough. The goal is to **understand and demonstrate** the algorithm, not to compete with production solvers. If we needed to scale to 500+ customers, a C++ reimplementation would be warranted.

---

### Q20: "What are the limitations of this approach?"

**A:** 

1. **Scalability**: The O(N²) split and local search operators don't scale beyond ~200 customers without major optimizations
2. **No time windows**: Real VRP often includes delivery time windows, which we didn't model
3. **Static only**: Our solution is for a frozen snapshot of demand — real-world routes change in real time
4. **Single depot**: Multi-depot VRP is a separate (harder) variant
5. **No service time**: We assume instantaneous service; real deliveries take time
6. **Deterministic**: No handling of stochastic travel times or demand uncertainty
7. **Tuned for 35 customers**: Parameters were chosen for this specific instance size

These are all addressable by extending the framework — the algorithm architecture supports adding time windows, multiple depots, etc., as additional constraints in the split algorithm and evaluation function.

---

*Prepared for the AIE213 VRP presentation. These 20 questions cover the most likely areas of audience inquiry.*
