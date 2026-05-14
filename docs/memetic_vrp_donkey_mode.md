# Memetic Algorithm Explained (The "Donkey Mode" Guide)

> *If you've ever wondered how a computer can figure out the best delivery routes for 35 houses using 5 trucks — and you want it explained like you're a complete beginner — this is for you.*

---

## What Problem Are We Actually Solving?

**Imagine this:** You run a pizza delivery service.

- You have **one kitchen** (the depot) in the center of town
- You have **35 hungry customers** scattered across the city
- You own **5 delivery scooters**, and each scooter can carry at most **80 kg of pizza**
- Each customer ordered a different amount of pizza (some 3 kg, some 20 kg — hungry people!)
- Every scooter must start at the kitchen, deliver, and come back
- You want to use the **least total fuel possible**

**That's the Vehicle Routing Problem (VRP).** The computer's job is to answer: *"Which scooter goes to which houses, in what order, so that no scooter is overloaded and we burn the least fuel?"*

---

## Why Is This Hard?

Because the number of possible ways to arrange 35 deliveries is **astronomical**.

If you tried to check every possible route combination one by one, even with a supercomputer, you'd be waiting until the **heat death of the universe**.

Here's the scale:

```
Number of customers   |   Possible route combinations
------------------------------------------------------
        5             |   ~120
       10             |   ~3,628,800
       20             |   ~2.4 × 10¹⁸  (2.4 quintillion)
       35             |   ~10⁴⁰         (more than atoms in the observable universe)
```

So we need to be **smart** about how we search. We can't try everything. We need a **metaheuristic**.

---

## Two Ways to Find a Good Route

Think of finding the best VRP solution as finding the **highest peak in a mountain range while blindfolded**.

### Method 1: Global Search — Like Sending Out Scouts

One approach: send out 60 scouts, drop them at random locations across the mountain range (random initial solutions). Each scout yells back how high they are (fitness evaluation). The scouts at higher altitudes "mate" (crossover) to produce new scouts near them, and occasionally a scout randomly jumps to a new spot (mutation).

Over time, scouts tend to cluster near high peaks.

**This is the Genetic Algorithm (GA) part.** It explores the whole mountain range, looking for promising areas.

**The problem:** Scouts might be near a peak but not quite at the summit. They drift around but never quite reach the top.

### Method 2: Local Search — Like Climbing Uphill

A different approach: wherever you are, just take the steepest step uphill. Keep doing that until every step you could take goes downhill. Congratulations, you're at a peak.

**This is Local Search.** It exploits the current position to reach the very best nearby solution.

**The problem:** You might be on a small hill (local optimum) while there's a much bigger mountain (global optimum) somewhere else. You can't see it because you only look at your immediate neighbors.

---

## The Memetic Algorithm: Best of Both Worlds

### The Analogy: A Football Team

Imagine you're building the world's best football team:

| What | Football Analogy | VRP Analogy |
|------|-----------------|-------------|
| **Genetic Algorithm** | You hold tryouts across the country, recruit diverse players, mix their strengths | Explores the whole search space, combines good solutions |
| **Local Search** | Each player does intense individual training to perfect their skills | Each solution is refined to its local optimum |
| **Memetic Algorithm** | You recruit widely AND train each player intensely | Explore broadly AND exploit locally |

### The Analogy: Writing an Essay

Think of writing a 10-page essay:

| Step | Essay Analogy | VRP Analogy |
|------|--------------|-------------|
| 1. Brainstorm | Get ideas from 60 different students (random population) | Generate 60 random tours |
| 2. Combine ideas | Take the best paragraphs from two students and merge them (crossover) | Order Crossover combines two tours |
| 3. Add variety | Shuffle some sentences around (mutation) | Swap/inversion mutation |
| 4. Edit & polish | A dedicated editor fixes grammar, improves transitions, tightens prose (local search) | 2-opt/Or-opt/Relocate refine each route |
| 5. Keep the best | Save the top 2 essays verbatim (elitism) | Keep best solutions unchanged |
| 6. Fresh ideas | If everyone's essays start looking the same, bring in new students (diversity injection) | Inject random tours when stagnant |

---

## How Our Memetic Algorithm Works (Step by Step)

### Step 1: Make Some Random Guesses

We start by creating 60 **random delivery sequences** (giant tours). Each sequence is just a shuffled list of all 35 customers:

```
Guess #1:  [12, 3, 27, 8, 19, ...]  →  "Visit customers in this order"
Guess #2:  [31, 15, 2, 22, 7, ...]  →  "No, visit them in THIS order"
... (58 more random guesses)
```

At this point, every guess is terrible. The best one is about **1246 fuel units**.

### Step 2: Turn Sequences into Actual Routes

A sequence like [12, 3, 27, 8, 19, ...] doesn't tell us which scooter does what. We need to **split** it into routes.

**Analogy:** You have one long shopping list but three shopping bags. You need to split the list so no bag gets too heavy.

The computer uses an algorithm called **Prins' Split** that finds the optimal way to cut the sequence into routes:

```
Before: [12, 3, 27, || 8, 19, 1, 15, || 22, 7, 9, ...]
          Scooter 1      Scooter 2          Scooter 3
```

The magic is: the computer checks every possible way to split and picks the one that uses the least total distance, while ensuring no scooter is overloaded.

### Step 3: Pick the Best, Combine Them

**Tournament Selection** (pick parents):

```
Randomly grab 3 guesses from the population:
  Guess A: costs 800 fuel
  Guess B: costs 550 fuel  ← Winner! Use this as Parent 1
  Guess C: costs 1200 fuel

Repeat → get Parent 2
```

**Order Crossover** (make babies):

```
Parent 1:  [A, B, C, D, E, F, G, H]
Parent 2:  [E, C, A, H, B, G, D, F]

Step 1: Copy a random chunk from Parent 1 to the baby:
         Baby: [_, _, C, D, E, _, _, _]

Step 2: Fill the blanks from Parent 2's order, skipping ones already there:
         Parent 2 order: E, C, A, H, B, G, D, F
         Skip: C, D, E (already in baby)
         Fill: A, H, B, G, F

Baby:    [A, H, C, D, E, B, G, F]
```

The baby inherits the **structure** from Parent 1 (the chunk) and the **order** from Parent 2. It keeps the best parts of both!

### Step 4: Add a Little Chaos

Occasionally (15% of the time), we randomize a route a tiny bit:

- **Swap**: "Trade customer #7 and customer #14 in the visit order"
- **Inversion**: "Reverse the order of houses 3 through 9"
- **Displacement**: "Move houses 4-5-6 to visit them after house 12 instead of before"

This is like **genetic mutation** — most mutations are bad, but occasionally one produces a slightly better route.

### Step 5: Polish, Polish, Polish (The "Memetic" Magic)

Here's where we go beyond a regular genetic algorithm. For **15% of the population** each generation, we put the routes through an intense **refinement process**:

#### 5a. 2-opt: "Stop Criss-Crossing!"

```
Bad route (crossed):              Good route (uncrossed):
    A ────────── D                    A ── B
    │            │                    │     │
    │     X      │        →           │     │
    │            │                    │     │
    B ────────── C                    D ── C
```

Crossed paths always waste distance. The 2-opt operator finds and removes these crossings by reversing the middle segment.

**Analogy:** You're walking through a supermarket aisles. Instead of zigzagging across the store, you go aisle by aisle in order. Same items visited, less walking.

#### 5b. Or-opt: "Move This Group"

```
Before:  House 1 → [House 2 → House 3 → House 4] → House 5 → House 6
After:   House 1 → House 5 → [House 2 → House 3 → House 4] → House 6
```

Sometimes visiting a group of nearby houses at a different point in the route saves fuel.

#### 5c. Relocate: "One Package to a Different Scooter"

```
Scooter A:  Kitchen → X → P → Y → Z → Kitchen
Scooter B:  Kitchen → U → V → W → Kitchen

Move customer P from Scooter A to Scooter B:
Scooter A:  Kitchen → X → Y → Z → Kitchen
Scooter B:  Kitchen → U → V → P → W → Kitchen
```

This balances the load and can dramatically improve total distance.

#### 5d. Exchange: "Swap Two Packages"

```
Scooter A has customer P, Scooter B has customer Q.
If swapping them makes both routes shorter AND keeps loads feasible → do it!
```

#### 5e. 2-opt*: "Cross-Connect Two Routes"

```
Scooter A: Kitchen → A1 → A2 → \[CUT\] → A3 → A4 → Kitchen
Scooter B: Kitchen → B1 → B2 → \[CUT\] → B3 → B4 → Kitchen

Reconnect:
Scooter A': Kitchen → A1 → A2 → B3 → B4 → Kitchen
Scooter B': Kitchen → B1 → B2 → A3 → A4 → Kitchen
```

### Step 6: Keep the Champions

The 2 best-performing solutions are **copied as-is** to the next generation. No mutation, no crossover — they're protected like endangered species. This is called **elitism**.

### Step 7: Fresh Blood When Needed

If the algorithm gets stuck (no improvement for 25 generations in a row), it injects **12 completely random new tours** into the population, replacing the worst ones.

**Analogy:** If every essay in class starts looking identical, bring in 12 new students who write completely differently. Maybe one of them has a fresh perspective that leads to a breakthrough.

### Step 8: Repeat

Steps 2-7 repeat for 150 generations. Each generation, the best solution tends to improve (or at least not get worse).

---

## The Results (What This Algorithm Achieves)

| Metric | Before | After |
|--------|--------|-------|
| Total distance | ~1246 units | ~514 units |
| Improvement | — | **58.7%** |
| Routes used | 5 scooters | 4 scooters (more efficient) |
| Capacity violations | None | None |
| Time to solve | — | ~55 seconds |

The algorithm essentially cuts fuel costs nearly in half compared to random assignment, while using fewer vehicles and respecting all capacity limits.

---

## Key Concepts Summary (The TL;DR)

| Concept | One-line explanation | Analogy |
|---------|---------------------|---------|
| **VRP** | Deliver to 35 houses with 5 trucks, minimize fuel | Pizza delivery logistics |
| **Metaheuristic** | Smart search when checking everything is impossible | Finding a needle in a haystack with a magnet, not your fingers |
| **Genetic Algorithm** | Evolve solutions like nature evolves species | Breeding better racehorses over generations |
| **Local Search** | Intensively improve one solution until it can't get better | Polishing a rough diamond until it sparkles |
| **Memetic Algorithm** | GA + Local Search = Explore globally, refine locally | Recruit athletes worldwide, then each one trains daily |
| **Giant Tour** | A list of all customers (no depot) | A shuffled deck of cards, one per customer |
| **Prins Split** | Smart algorithm that cuts one long list into feasible routes | Filling shopping bags without overloading any |
| **Crossover** | Combine two good solutions to make a new one | Mixing the best paragraphs from two essays |
| **Mutation** | Randomly tweak a solution slightly | Shuffling a few cards to see if the hand improves |
| **2-opt** | Remove route crossings | Uncrossing tangled headphone wires |
| **Relocate** | Move a customer to a different truck | "Hey, can you deliver this one on your way?" |
| **Elitism** | Always keep the best solutions | Hall of Fame — the best players never get cut |
| **Diversity injection** | Add random solutions when stuck | Bringing in rookies when the veterans are in a slump |

---

## Why This Is Cool

This algorithm works because it mimics **two types of evolution at the same time**:

1. **Biological evolution** (genes cross over, mutate, compete) — explores all possibilities
2. **Cultural evolution** (ideas are refined, improved, optimized through learning) — perfects each possibility

Just like how humans evolved biologically over millions of years, but also learned to build rockets in a single lifetime through cultural learning — the memetic algorithm evolves solutions broadly AND refines them finely.

---

*The "Donkey Mode" Guide — because everyone deserves to understand cool algorithms. : )*
