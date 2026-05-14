# Presentation Script: Memetic Algorithm for Vehicle Routing

## Timing & Slide Guide

**Total duration:** ~12-14 minutes (adjust pacing as needed)
**Slides:** 20

---

## SLIDE 1: Title & Hook (~45 seconds)

### VISUAL ON SCREEN: Dark title slide — "Optimizing the Last Mile" + subtitle

---

**SAY:**

> "Optimizing the Last Mile — Solving the Vehicle Routing Problem in Modern Logistics.

> Here's the problem. You run a delivery company with one warehouse, 35 customers scattered across a city, and 5 trucks. Each truck has a weight limit. Every customer ordered a different amount. You need one answer: which truck goes where, in what order, to burn the least fuel?

> Simple question, right? But with just 35 stops, there are more possible route combinations than atoms in the observable universe. You cannot check them all. So we need a smart search strategy. That's where the **memetic algorithm** comes in — a hybrid of genetic evolution and targeted local search. I'm going to walk you through how we built one."

---

### TRANSITION:

> "Let's start with the challenge we're up against."

---

## SLIDE 2: Section Title — The Challenge (~15 seconds)

### VISUAL ON SCREEN: Section divider — "The Challenge of Modern Logistics"

---

**SAY:**

> "In a world demanding faster, cheaper deliveries — how do we efficiently connect the warehouse to the customer's door? That's the Vehicle Routing Problem."

---

## SLIDE 3: What is the VRP? (~60 seconds)

### VISUAL ON SCREEN: Two-column tiled text — Goal & Applications (left), Complexity (right)

---

**SAY:**

> "Let me define the problem precisely.

> **[Point to left tile]** The Vehicle Routing Problem asks: given a depot, a fleet of vehicles, and a set of customers — each with a location and a demand — find the set of routes that serves every customer exactly once, never exceeds any vehicle's capacity, and minimizes total travel distance.

> This is the math that powers Amazon's same-day delivery, UPS's package routing, waste collection schedules — any system where you dispatch vehicles to serve points on a map.

> **[Point to right tile]** Now the catch: VRP extends the Traveling Salesman Problem and is **NP-hard**. As you add customers, the number of possible routes explodes factorially. Brute force is mathematically impossible for real-world instances. 35 customers is already beyond exhaustive search.

> So we need algorithms that find near-optimal solutions without checking every possibility. That's what the rest of this presentation is about."

---

### TRANSITION:

> "First, let's look at why this problem actually matters — in dollars and emissions."

---

## SLIDE 4: Real-World Impact (~45 seconds)

### VISUAL ON SCREEN: Two image tiles — Emissions reduction chart (left), Cost savings chart (right)

---

**SAY:**

> "VRP optimization isn't academic. It has enormous real-world impact.

> **[Point to left] Efficient routing directly cuts CO2 emissions.** UPS's ORION routing system alone prevents over 100,000 metric tons of CO2 annually — just by eliminating unnecessary miles.

> **[Point to right]** The financial side is equally compelling. Shaving just one mile off each driver's daily route translates to roughly 50 million dollars per year for large global fleets. Route optimization is one of the highest-ROI investments a logistics company can make.

> This is why companies invest millions in solving this problem well."

---

### TRANSITION:

> "So what makes this problem hard? Let's look at the constraints."

---

## SLIDE 5: Key Problem Constraints (~45 seconds)

### VISUAL ON SCREEN: Three tiled icons — Time Windows, Capacity Limits, Dynamic Traffic

---

**SAY:**

> "Real-world VRP has constraints that compound the difficulty.

> **[Point to each in turn]** Time windows — customers want deliveries in specific slots. Miss the window, pay a penalty. Capacity limits — every truck has a maximum payload by weight and volume. And dynamic traffic — routes must account for congestion, road closures, weather.

> Each constraint you add makes the problem combinatorially harder. A basic VRP might be tractable. Add time windows, capacity, and real-time traffic, and you're firmly in metaheuristic territory — which is where we're headed."

---

### TRANSITION:

> "Let's look at the approaches available to us."

---

## SLIDE 6: Section Title — Approaches (~15 seconds)

### VISUAL ON SCREEN: Section divider — "Mathematical & Algorithmic Approaches"

---

**SAY:**

> "How do we actually solve an NP-hard problem in practice? There are three broad strategies."

---

## SLIDE 7: Solving the VRP — Three Approaches (~60 seconds)

### VISUAL ON SCREEN: Three image tiles — Exact Methods (left), Heuristics (center), Metaheuristics (right)

---

**SAY:**

> "**[Point to left]** First, **exact methods** — things like branch-and-cut, integer linear programming. These guarantee finding the absolute optimal solution. But they only work for very small instances. Beyond about 50 customers, computation time becomes impractical.

> **[Point to center]** Second, **heuristics** — rule-of-thumb algorithms like the Nearest Neighbor method or Clarke-Wright savings. They're fast — seconds — but they give you about 75% of optimal quality. Good enough for quick dispatch, not great for fleet planning.

> **[Point to right]** Third, **metaheuristics** — advanced frameworks like Genetic Algorithms or Simulated Annealing. These don't guarantee optimality, but they get you within a few percent of the best possible answer, in minutes instead of days. This is the sweet spot for real logistics.

> That's where our work sits."

---

### TRANSITION:

> "Here's how these approaches stack up."

---

## SLIDE 8: Algorithm Performance Comparison (~45 seconds)

### VISUAL ON SCREEN: Horizontal bar chart — Exact (100%, hours), Memetic (58.7% improvement, 55s), Heuristics (fast baseline, seconds)

---

**SAY:**

> "This bar chart visualizes the trade-off.

> **[Point to top bar]** Our memetic algorithm achieves a 58.7% improvement over random initialization — taking a 35-customer instance from 1,246 distance units down to 514 — in about 55 seconds. That's competitive quality in under a minute.

> **[Point to middle bar]** Exact methods give 100% optimality but take hours or days — unusable for daily dispatch.

> **[Point to bottom bar]** Basic heuristics run in seconds but leave significant distance on the table.

> The memetic algorithm sits right where modern logistics needs it: strong optimization quality at operational speed. And unlike a black-box solver, we can explain exactly how it works."

---

### TRANSITION:

> "Before we dive into the algorithm, let me quantify what we're saving ourselves from."

---

## SLIDE 9: The Cost of Inefficiency (~45 seconds)

### VISUAL ON SCREEN: Large "15%" number (left), cost breakdown grid (right)

---

**SAY:**

> "What's the cost of **not** optimizing? About 15% excess fuel burned.

> **[Point to right grid]** For a regional fleet of just 100 trucks, driving an inefficient extra 15 miles per day yields: about 60,000 excess gallons of fuel annually, over $240,000 in wasted operating capital, and 600 metric tons of extra CO2. That's the 'do-nothing' penalty.

> Optimization isn't a luxury — it directly converts to money saved and emissions prevented. That's why we built this algorithm."

---

### TRANSITION:

> "Now let me show you our solution. This is a **memetic algorithm** — a Genetic Algorithm combined with local search."

---

## SLIDE 10: Our Approach — Memetic Algorithm Overview (~75 seconds)

### VISUAL ON SCREEN: Two-column — bullet points (left), `diagram_architecture.png` (right)

---

**SAY:**

> "Why a memetic algorithm specifically for VRP? Two reasons.

> First, the VRP search space is enormous and rugged — lots of local optima. Think of it like a mountain range with thousands of peaks. A pure genetic algorithm would explore broadly but converge too slowly — it'd find the general region of the high peaks but never quite reach any summit. Pure local search would climb the nearest hill and stop, even if a much bigger mountain is nearby. Neither alone is sufficient.

> A memetic algorithm does both: the GA **explores** globally, the local search **exploits** locally. The GA jumps between regions; the local search climbs each region to its precise peak. Together they find both the right mountain and the exact summit. Moscato coined the term in 1989 — memes evolve culturally through learning, just like we refine solutions through local search, on top of the biological evolution from crossover and mutation.

> **[Point to diagram]** Here's our architecture. Left side: the GA loop — a population of 60 solutions, tournament selection, Order Crossover, and three mutation types. Right side: the local search — five VRP-specific operators that refine promising offspring.

> Key features: we encode solutions as **giant tours** decoded by **Prins' split algorithm**, apply local search to 15% of the population each generation, preserve elite solutions via elitism, and inject random diversity when stagnation is detected.

> This runs for 150 generations. Let me break down each component."

---

### TRANSITION:

> "First: how do we even represent a VRP solution so the GA can operate on it?"

---

## SLIDE 11: Encoding — Giant Tour + Prins Split (~75 seconds)

### VISUAL ON SCREEN: Two-column — explanation (left), `diagram_encoding.png` (right)

---

**SAY:**

> "In VRP, a solution has two layers: which customers go to which vehicle, and in what order each vehicle visits them. That's hard to encode directly.

> **[Point to diagram Step 1]** Our approach uses a **giant tour** — a simple permutation of all 35 customers. Think of it as a shuffled deck of cards. Each card is a customer ID. The order in the deck matters — customers early in the list tend to end up on earlier routes.

> **[Point to Step 2]** But a single list doesn't say where one vehicle stops and the next begins. That's where **Prins' Split Algorithm** comes in. Prins showed in 2004 how to partition a giant tour into feasible routes optimally. Here's how: it builds a graph with 36 nodes (0 to 35, representing positions in the giant tour). For every pair i < j, it asks: can customers at positions i+1 through j fit in one vehicle? If yes, it adds an edge with the route cost as its weight. Then it finds the shortest path from node 0 to node 35 using dynamic programming — this is exactly like finding the cheapest way to cut the giant tour into pieces, where each piece is a feasible route.

> The cost of a single edge is this: depot to first customer, then customer-to-customer for each consecutive pair in the segment, then last customer back to depot. The DP algorithm is O(N²), which for 35 customers means about 1,225 edge checks — trivial computation.

> **[Point to Step 3]** The output is a set of colored routes. Each route starts and ends at the depot, doesn't exceed capacity, and collectively visits every customer.

> This is elegant because the GA only needs to work on 1D permutations — which is mathematically well-understood. All the VRP-specific complexity is handled by the split decoder."

---

### TRANSITION:

> "Now, how does the GA actually evolve these giant tours? The key operator is Order Crossover."

---

## SLIDE 12: Order Crossover (OX) (~60 seconds)

### VISUAL ON SCREEN: Array visualization with 4 steps (built into the slide HTML)

---

**SAY:**

> "Order Crossover, or OX, combines two parent giant tours into a child. It operates directly on the permutation — no routes, no vehicles, just the visit order.

> Why OX specifically? Standard one-point or two-point crossover doesn't work for permutations — they'd create duplicate customers and lose others. You'd end up with a route that says 'visit customer 3 twice, customer 7 zero times.' That's invalid for VRP. OX is designed to avoid this — it preserves all customers exactly once.

> Here's how it works. **[Walk through the 4 steps on screen]**

> **Step 1:** Take a random contiguous segment from Parent 1 — say, customers 3, 4, 5 in positions 2 through 4. That swath gets copied directly to the child. This preserves the **relative adjacency** of these customers — because in a good solution, nearby customers in the permutation tend to be served by the same vehicle.

> **Step 2:** Now look at Parent 2's sequence: 7, 6, 5, 4, 3, 2, 1. We're going to use this to fill the gaps.

> **Step 3:** The child currently has blanks where the swath wasn't. The swath [3, 4, 5] is locked in.

> **Step 4:** Starting from the right cut point, read Parent 2 in order — 7, 6, 2, 1. Skip 5, 4, 3 because they're already in the child. Fill the blanks. Result: [2, 1, 3, 4, 5, 7, 6].

> The child inherits the **contiguous structure** of Parent 1's swath and the **relative order** of Parent 2. No customer appears twice, none are lost. This preserves valid permutations — every customer appears exactly once in the child."

---

### TRANSITION:

> "That gives us new offspring. But here's what makes this algorithm *memetic* — we don't just breed and move on. We train each offspring through local search."

---

## SLIDE 13: Local Search — 5 Operators (~90 seconds)

### VISUAL ON SCREEN: Two-column — explanation (left), `diagram_local_search.png` (right)

---

**SAY:**

> "This is the heart of the memetic algorithm. Each generation, 15% of offspring go through an intensive local search pipeline using five operators.

> Let me explain what makes these operators fast — **delta evaluation**. Normally, evaluating a move would mean recomputing the full route distance from scratch — summing all edge costs along the route, O(L) per evaluation. With 35 customers and hundreds of move checks per individual, this gets expensive.

> Delta evaluation computes only the **change** in cost. For example, relocating customer X from route A to route B: instead of recomputing both 9-customer routes fully, we compute: new cost of A = old A minus edges involving X plus the new connection that bridges the gap. New cost of B = old B plus edges involving X at the insertion point minus the edges that get broken. This is O(1) per move instead of O(L). It gives a 3-10x speedup — which is what brought our runtime from 162 seconds to 55.

> **[Point to top row of diagram]** The operators split into two categories. **Intra-route** — these work inside a single vehicle's route:
> - **2-opt:** tries reversing every possible subtour segment. If the reversal shortens the route, it's kept. 2-opt explores the '2-exchange' neighborhood — every pair of edges that could be swapped. For a route of length 9, that's about 28 pairs to check. A single pass removes the most obvious crossings, and repeating it converges to the optimal 2-opt solution — a locally shortest route with no crossings.
> - **Or-opt:** takes a short segment of 2-3 consecutive customers and tests moving it to every other position within the route. It's like asking: 'would these three customers be better served earlier or later in this trip?' Or-opt explores a larger neighborhood than 2-opt, so it can find improvements 2-opt misses.

> **[Point to bottom row of diagram] Inter-route** — these move work between different vehicles:
> - **Relocate:** tries moving each customer from its current route to every possible insertion point in every other route. Only accepts moves that don't violate capacity. This is the most intuitive operator — rebalancing load.
> - **Exchange:** swaps two customers between two different routes. The mutual swap neighborhood is larger than relocate — for each pair of routes, it checks every customer-on-customer combination, about 9×9 = 81 swaps for two average routes.
> - **2-opt\*:** splits two routes at every possible pair of cut points and cross-connects them. This creates the largest structural change — effectively redesigning the boundary between two vehicle territories. It's one of the most powerful moves but also the most expensive: about 10×10 = 100 cut combinations per route pair.

> These five operators run in sequence — intra-route first (cheaper, refines individual routes), then inter-route (more expensive, reshapes the fleet). The cycle repeats up to three times or until no operator can find an improvement. The combined neighborhood covers every meaningful modification to a VRP solution — no single operator could cover all these cases alone."

---

### KEY POINT TO EMPHASIZE:

> "The insight that makes memetic algorithms powerful: the GA jumps between different regions of the search space — global exploration. The local search climbs to the very peak of whatever hill it lands on — local exploitation. Neither works alone. Together, they're far stronger."

---

### TRANSITION:

> "Let me show you the full generation cycle and what happens when we run 150 generations."

---

## SLIDE 14: Iteration & Convergence (~60 seconds)

### VISUAL ON SCREEN: Two-column — numbered steps (left), `memetic_vrp_final.png` convergence section (right)

---

**SAY:**

> "Each generation follows this cycle:

> **Step 1 — Evaluate:** Compute fitness for all 60 individuals via Prins Split. Fitness equals total distance of all decoded routes plus a penalty for capacity violations. The penalty formula is: 1,000 plus 5 times the generation number, multiplied by the total overload. So at generation 0, the penalty is 1,000 per unit of overload. At generation 150, it's 1,750. This starts soft to allow exploration of interesting but slightly overloaded solutions, and gradually hardens to enforce strict feasibility by the end.

> **Step 2 — Select and Breed:** Tournament selection picks parents. Here's how: randomly grab 3 individuals from the population, pick the one with the shortest total distance. Do this twice to get two parents. This is called tournament size 3 — selective enough that fitter individuals reproduce more often, but not so selective that diversity collapses. Then Order Crossover combines them to produce offspring. After crossover, mutation adds random variation. We have three mutation types applied 15% of the time total: **swap mutation** exchanges two random customers in the tour. **Inversion mutation** reverses a random subsequence — this is useful because reversal in the giant tour corresponds to reversing a segment of a vehicle's route, which 2-opt would normally need to discover. **Displacement mutation** cuts a subsequence and reinserts it elsewhere — this can move a cluster of customers from one vehicle to another.

> **Step 3 — Local Search:** 15% of offspring undergo the full five-operator pipeline. These are the 9 or so offspring that are promising but not yet locally optimal. The local search polishes them until every operator finds no further improvement.

> **Step 4 — Elitism:** The top 2 solutions are preserved unchanged to the next generation. Without elitism, the best solution could be lost if crossover happens to recombine it poorly. With elitism, we guarantee monotonic improvement — the best fitness never gets worse.

> **Step 5 — Diversity Injection:** If 25 generations pass with no fitness improvement, 20% of the population (except the elites) is replaced with completely random giant tours. This is a hard reset that prevents the GA from wasting compute on a converged, identical population. The random tours are then exposed to local search in subsequent generations, which pulls them toward whatever local optimum they're nearest to. Occasionally one of these injections finds a better basin than the current one.

> **[Point to convergence image]** The right panel shows the result. The blue line is the best fitness — notice the dramatic drop in the first 30 generations, from 1,246 to 514. That's a 58.7% improvement. After that, the algorithm plateaus — it's found a deep local optimum that even diversity injection can't escape. The orange line is the average population fitness — notice the periodic spikes near generations 47, 72, 97, and 122. Those are from diversity injection: random tours are much worse on average, so the average jumps up, then the local search pulls them back down."

---

### TRANSITION:

> "So what does the final solution actually look like? Let's look at the results."

---

## SLIDE 15: Results Dashboard (~60 seconds)

### VISUAL ON SCREEN: Two-column — stats table (left), `memetic_vrp_final.png` route map (right)

---

**SAY:**

> "Here are the concrete numbers from our run on a 35-customer instance.

> **[Point to table]** Initial distance: 1,246 units. Final distance: 514 units. That's a 58.7% reduction — nearly 60% less fuel. Four routes used out of five available vehicles. Zero capacity violations — every truck is within its weight limit. Computation time: about 55 seconds. Population of 60, 150 generations, 15% local search intensity.

> **[Point to route map]** The map tells the visual story. The black square is the depot. Each color is a different vehicle. Notice three things: no routes cross unnecessarily, customers are naturally grouped into geographic clusters — the algorithm discovered these on its own — and the routes stay near their region instead of zigzagging across the map.

> The algorithm effectively reduced a randomly initialized 5-route, 1,246-unit mess into a clean 4-route, 514-unit solution. All constraints satisfied."

---

### TRANSITION:

> "Let me highlight four technical choices that made this efficient and effective."

---

## SLIDE 16: Key Technical Innovations (~45 seconds)

### VISUAL ON SCREEN: Bullet list with icons — 4 innovations

---

**SAY:**

> "Four innovations worth highlighting:

> **Delta evaluation:** Instead of recomputing full route costs for every move, we compute only the difference — old minus new. For the exchange operator, this means checking 4 distances instead of recomputing two routes of 9 nodes each: 4 operations versus 18. For relocate, it's 3 distance lookups for the delta versus 8 for a full route cost. Across thousands of move checks per generation, these O(1) savings compound to a 3-10x speedup — the difference between a 162-second runtime and a 55-second one.

> **Adaptive penalty:** The penalty function is λ(g) = 1,000 + 5g, where g is the generation number. At generation 0, λ = 1,000 — an overcapacity of 1 unit adds 1,000 distance units to the fitness. This is strict enough to discourage infeasibility but not so strict that it blocks exploration. At generation 150, λ = 1,750 — nearly double, forcing solutions toward strict feasibility. The linear increase means the algorithm naturally transitions from 'find promising regions' early on to 'deliver a valid solution' by the end.

> **Diversity injection:** Stagnation detection with automatic population refresh. We track how many generations pass since the best fitness last improved. When that counter hits 25, we replace 12 out of 60 individuals (the bottom 20%, excluding the 2 elite solutions) with completely new random permutations. The random tours are then exposed to local search in subsequent generations. You can see this on the convergence curve as periodic spikes in the average fitness — the average jumps when random tours enter, then drops as local search refines them. Without this mechanism, the population would converge to identical clones by generation 40, wasting 110 generations of compute.

> **Prins Split decoding:** Clean separation of concerns — the GA operates on simple 1D permutations, the split handles all VRP complexity: multiple vehicles, capacity constraints, route distance computation. This separation means you can extend the framework to new VRP variants by changing only the decoder. Want to add time windows? Modify the split algorithm to penalize late arrivals, keep the GA unchanged. Want to add multiple depots? Change the split to assign customers to the nearest depot. The encoding is the hard part in evolutionary computation — Prins' insight was that fixing a good encoding makes everything else tractable."

---

### TRANSITION:

> "Let me zoom out and talk about where VRP optimization is heading."

---

## SLIDE 17: Emerging VRP Solutions (~30 seconds)

### VISUAL ON SCREEN: Bullet list with icons — AI, Dynamic Re-Routing, Drones

---

**SAY:**

> "VRP research isn't standing still. Three trends to watch:

> AI and machine learning are moving from static routing to predictive models — forecasting traffic, weather, even parking availability before dispatching.

> Dynamic re-routing is shifting from overnight batch processing to real-time adjustments — recalculating routes on the fly as new orders come in or delays occur.

> And drone integration — the VRP with Drones variant — is an active frontier where algorithms orchestrate trucks launching and retrieving drones for rural last-mile delivery."

---

## SLIDE 18: Why VRP Remains an Open Challenge (~30 seconds)

### VISUAL ON SCREEN: Two-column tiled text

---

**SAY:**

> "Two reasons VRP is still actively researched.

> First — there is no perfect solution. NP-hardness means the mathematical optimum is unreachable for real instances. Researchers are perpetually hunting for algorithms that get closer to optimal, faster.

> Second — the real world keeps adding complexity. Electric vehicles with charging constraints. Multi-modal drone operations. Split-second live recalculation for thousands of vehicles. Each new dimension spawns new research problems.

> The framework we built — GA plus local search with Prins split encoding — can be extended to these variants. That's the power of a modular architecture."

---

## SLIDE 19: The Evolution of Routing (~30 seconds)

### VISUAL ON SCREEN: Timeline with 6 milestones

---

**SAY:**

> "Let me put this in historical context.

> **[Walk timeline left to right]** The TSP was mathematically formulated in the 1930s. Dantzig and Ramser defined the Vehicle Routing Problem in 1959. The 1980s and 90s brought computing power and the era of heuristics. In 1989, Moscato introduced Memetic Algorithms — the hybrid approach we used. In 2004, Prins proposed the Giant Tour plus Split encoding. And today, cloud computing and machine learning are redefining real-time fleet management.

> Our work sits in this lineage — applying Moscato's memetic framework to Prins' VRP encoding, with modern optimizations like delta evaluation and diversity injection."

---

### TRANSITION:

> "Let me wrap up."

---

## SLIDE 20: Q&A (~15 seconds intro, then open floor)

### VISUAL ON SCREEN: Large "Questions?" + thank you message

---

**SAY:**

> "To summarize: we built a memetic algorithm for the Capacitated Vehicle Routing Problem. Genetic algorithm for global exploration. Five local search operators for intensive refinement. Prins' split for decoding. Delta evaluation for speed. Diversity injection for robustness. The result: 58.7% distance reduction, zero capacity violations, in under a minute.

> **[If time, let `memetic_vrp_evolution.gif` play in the background on this slide]**

> Thank you. I'm happy to take your questions."

---

## Q&A Preparation — Common Questions & Answers

### Q1: "How do you know the solution is good enough? Is it optimal?"

> **A:** We can't guarantee optimality — VRP is NP-hard so no polynomial-time algorithm can. However, the 58.7% improvement over random initialization and the convergence behavior (stable plateau after rapid improvement) suggests we're very close to a local optimum. For the 35-customer instance, the Clarke-Wright savings heuristic would typically score in the 550-600 range, so our 514 result is competitive.

### Q2: "Why 150 generations? Why not 500 or 50?"

> **A:** 150 is a practical balance. The solution converges by generation 30. After that, 120 more generations give diversity injection time to potentially escape local optima, while keeping runtime under 1 minute. With early stopping (halt after 40 gens of no improvement), we could cut runtime nearly in half with identical results.

### Q3: "Why use a giant tour instead of directly encoding routes?"

> **A:** Direct route encoding is messy for genetic operators — crossover of variable-length, variable-count routes is complex. The giant tour is a fixed-length permutation, which is well-studied in evolutionary computation. The Prins split algorithm handles all feasibility and routing, cleanly separating encoding from evaluation. This was Prins' key insight in 2004.

### Q4: "What happens if the constraints can't be satisfied?"

> **A:** Our penalty-based approach allows temporarily infeasible solutions but penalizes them heavily. The adaptive penalty increases with generations, enforcing strict feasibility by the end. If the instance is truly infeasible (total demand exceeds fleet capacity), the algorithm converges to the least-infeasible solution and reports violations explicitly.

### Q5: "How does this scale to 200 customers?"

> **A:** The Prins split is O(N²) per evaluation, so 200 customers would be about 33x slower per evaluation than 35. We'd need to reduce population size, reduce local search intensity, and possibly use a faster split variant. The framework is scalable but would need parameter tuning. For 1000+ customers, you'd switch to ALNS-style approaches rather than pure population-based GA.

### Q6: "What's new about your implementation vs. existing VRP solvers?"

> **A:** This is an educational implementation demonstrating memetic algorithm principles. Production solvers like Google OR-Tools use more sophisticated techniques. Our contribution is the clean integration of GA + LS with delta evaluation, diversity injection, adaptive penalties, and comprehensive visualization — making the algorithm transparent, explainable, and suitable for learning.

---

## Presentation Tips

1. **Practice the transitions** — they connect the narrative and signal to the audience that we're moving to a new concept
2. **Point at the diagrams** when you refer to specific components — don't just talk at the slide
3. **Use analogies** from the Donkey Mode guide if the audience needs simpler explanations: "shuffled deck of cards" for giant tour, "tangled headphones" for 2-opt, "football tryouts + training" for memetic algorithm
4. **Be ready to skip slides** if running short on time — slides 4, 5, 9, 17, and 18 can be compressed to 15 seconds each or skipped without breaking the narrative
5. **The GIF animation** (`memetic_vrp_evolution.gif`) is your best visual — let it play during the conclusion slide
6. **Know your numbers**: 35 customers, 60 population, 150 generations, 5 operators, 58.7% improvement, 55 seconds, 4 routes, zero violations
7. **If someone asks about the code**, direct them to `memetic_algorithm_vrp.py` in the project repository — it runs with a single command

---

## Slide Checklist

| # | Topic | Visual | Key Image |
|---|-------|--------|-----------|
| 1 | Title & Hook | Dark title slide | — |
| 2 | The Challenge (section) | Section divider | — |
| 3 | What is VRP? | Two tiled columns | — |
| 4 | Real-World Impact | Two image tiles | Emissions/cost charts |
| 5 | Key Constraints | Three icon tiles | — |
| 6 | Approaches (section) | Section divider | — |
| 7 | Solving VRP | Three image tiles | exact/heuristic/meta |
| 8 | Algorithm Comparison | Bar chart | Actual metrics |
| 9 | Cost of Inefficiency | Big number + grid | 15% stat |
| 10 | Our MA Approach | Two-column | `diagram_architecture.png` |
| 11 | Encoding & Split | Two-column | `diagram_encoding.png` |
| 12 | Order Crossover | Array visualization | Built-in OX cells |
| 13 | Local Search (5 ops) | Two-column | `diagram_local_search.png` |
| 14 | Iteration & Convergence | Two-column | Convergence plot |
| 15 | Results Dashboard | Two-column | `memetic_vrp_final.png` |
| 16 | Key Innovations | Bullet list | — |
| 17 | Emerging Solutions | Bullet list | — |
| 18 | Why VRP Open | Two tiled columns | — |
| 19 | Evolution Timeline | Timeline | 6 milestones |
| 20 | Q&A | Questions + GIF | `memetic_vrp_evolution.gif` |

---

*Script prepared for AIE213 — Optimization Methods presentation.*
*GitHub: github.com/fourarms4x4/memetic-algo-opt*
