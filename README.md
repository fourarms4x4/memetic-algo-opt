# Memetic Algorithm for Vehicle Routing Problem (CVRP)

A memetic algorithm (Genetic Algorithm + Local Search) that solves the Capacitated Vehicle Routing Problem. Built for the AIE213 Optimization Methods course.

## What it does

Given a depot, 35 customers (each with a location and delivery demand), and 5 trucks with weight limits — finds the shortest set of delivery routes that serves everyone without overloading any vehicle.

## Results

| Metric | Value |
|--------|-------|
| Initial distance | 1,246 units |
| Final distance | 514 units |
| Improvement | **58.7%** |
| Routes used | 4 / 5 available |
| Capacity violations | 0 |
| Runtime | ~55 seconds |

## Quick start

```bash
# Run the VRP solver
python src/memetic_algorithm_vrp.py

# Regenerate diagrams
python src/generate_diagrams.py

# View the presentation
open presentation/index.html
```

## How it works

**Encoding:** Solutions are *giant tours* — permutations of all customers. The Prins Split algorithm decodes a giant tour into capacity-feasible multi-vehicle routes.

**Genetic Algorithm (exploration):**  
Population of 60, tournament selection, Order Crossover (OX), 3 mutation types, 150 generations.

**Local Search (exploitation — the memetic part):**  
15% of offspring per generation undergo 5 refinement operators:
- **Intra-route:** 2-opt (uncross paths), Or-opt (relocate segments)
- **Inter-route:** Relocate (move customer between trucks), Exchange (swap customers), 2-opt\* (cross-connect routes)

**Key features:**
- Delta evaluation (3-10x speedup over full recomputation)
- Adaptive penalty (softens capacity constraints early, enforces them late)
- Diversity injection (refreshes stale population with random tours)
- Elitism (preserves top 2 solutions each generation)

## Directory structure

```
├── src/                          # Source code
│   ├── memetic_algorithm_vrp.py  # VRP solver (main)
│   ├── memetic_algorithm_tsp.py  # TSP solver (bonus)
│   └── generate_diagrams.py      # Diagram generator
├── docs/                         # Documentation
│   ├── memetic_vrp_documentation.md
│   ├── memetic_vrp_donkey_mode.md
│   ├── memetic_vrp_presentation_script.md
│   └── memetic_vrp_qa.md
├── diagrams/                     # Generated diagrams
│   ├── diagram_architecture.png
│   ├── diagram_encoding.png
│   ├── diagram_flowchart.png
│   └── diagram_local_search.png
├── outputs/                      # Rendered results
│   ├── memetic_vrp_final.png
│   ├── memetic_vrp_evolution.gif
│   ├── memetic_tsp_final.png
│   └── memetic_tsp_evolution.gif
└── presentation/                 # HTML slides
    ├── index.html
    └── assets/
```

## References

- **Prins, C. (2004).** *A simple and effective evolutionary algorithm for the vehicle routing problem.* Computers & Operations Research, 31(12), 1985-2002.
- **Moscato, P. (1989).** *On Evolution, Search, Optimization, Genetic Algorithms and Martial Arts: Towards Memetic Algorithms.* Caltech C3P Report 826.
