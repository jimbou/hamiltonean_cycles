Here’s a concise **README.md** you can include with your submission — it connects your Python experiment to your presentation (“Undirected Hamiltonian Cycle is NP-Complete”) and the *Theory of Computation* course project:

---

# Parameterized Hamiltonicity — Exploring How Graph Constraints Affect Complexity

**Author:** Dimitrios Stamatios Bouras
**Course:** *Theory of Computation*, Peking University — School of Computer Science
**Date:** Fall 2025

---

##  Overview

This project studies how **structural constraints on graphs** affect the difficulty of finding a **Hamiltonian Cycle (HC)**.
It builds upon the theoretical foundation presented in *“Undirected Hamiltonian Cycle is NP-Complete: Why the Middle Vertex Enforces Direction”* and extends it experimentally.

While Hamiltonicity is NP-complete in general, some graph families make the problem tractable, while others remain hard even under strong restrictions.
The project combines **theoretical complexity analysis** and **empirical timing experiments**.

---

##  Goals

1. Demonstrate the **boundary between easy and hard graph classes** for Hamiltonian Cycle.
2. Show that certain constraints (e.g., bounded treewidth, low degree) make the problem polynomial-time solvable.
3. Visualize runtime growth empirically for multiple graph families.

---

##  Graph Families Studied

| Category   | Graph Type                    | Theoretical Complexity           |
| ---------- | ----------------------------- | -------------------------------- |
| **Easier** | Degree ≤ 2                    | P (linear-time structural check) |
|            | Tournaments                   | P (Camion’s Theorem — SCC test)  |
|            | Bounded Treewidth             | FPT — (T(n)=O(f(tw)\cdot n))     |
| **Harder** | Bipartite                     | NP-Complete                      |
|            | Planar                        | NP-Complete                      |
|            | Planar + Bipartite + Subcubic | NP-Complete                      |

---

##  Implementation

### Requirements

Install dependencies:

```bash
pip install networkx matplotlib
```

### Run the benchmark

```bash
python benchmark_driver.py
```

This script:

1. Generates random graphs for each class (NetworkX).
2. Runs the appropriate Hamiltonian-cycle solver:

   * Linear-time checks for easy cases.
   * Subset-DP (Held–Karp) for exponential ones.
3. Measures runtime across sizes and saves results.

Output folders:

```
benchmarks/
 ├─ benchmark_results.csv        # timing data
 └─ plots/
     ├─ deg_le2_time.png
     ├─ tournaments_time.png
     ├─ lowtw_time_vs_n.png
     ├─ bipartite_time.png
     ├─ planar_time.png
     ├─ pbs_time.png
     ├─ lowtw_time_vs_k_fixed_n.png
     └─ lowtw_time_vs_n_fixed_k.png
```

---

##  Plots Explained

| Plot                          | Description                                | Growth Trend      |
| ----------------------------- | ------------------------------------------ | ----------------- |
| `deg_le2_time.png`            | Linear-time check — single cycle detection | Flat              |
| `tournaments_time.png`        | Strong-connectivity test (Camion)          | Flat              |
| `lowtw_time_vs_n.png`         | FPT DP, treewidth≈√n                       | Mild              |
| `bipartite_time.png`          | Exponential DP runtime                     | Steep             |
| `planar_time.png`             | NP-hard, exponential                       | Steep             |
| `pbs_time.png`                | NP-hard even with strong limits            | Steep             |
| `lowtw_time_vs_k_fixed_n.png` | Fixed n, vary treewidth                    | Exponential in tw |
| `lowtw_time_vs_n_fixed_k.png` | Fixed tw, vary n                           | Linear in n       |

---

##  Interpretation

* **Low-degree, dense, or tree-like** structures simplify Hamiltonicity.
* **Combinatorially rich** structures (planar, bipartite) preserve NP-hardness.
* The **plots visualize the theory**: easy families show linear-time behavior, while NP-complete ones exhibit exponential growth.

---

Here’s a concise **README.md** you can include with your submission — it connects your Python experiment to your presentation (“Undirected Hamiltonian Cycle is NP-Complete”) and the *Theory of Computation* course project:

---

# Parameterized Hamiltonicity — Exploring How Graph Constraints Affect Complexity

**Author:** Dimitrios Stamatios Bouras
**Course:** *Theory of Computation*, Peking University — School of Computer Science
**Date:** Fall 2025

---

##  Overview

This project studies how **structural constraints on graphs** affect the difficulty of finding a **Hamiltonian Cycle (HC)**.
It builds upon the theoretical foundation presented in *“Undirected Hamiltonian Cycle is NP-Complete: Why the Middle Vertex Enforces Direction”* and extends it experimentally.

While Hamiltonicity is NP-complete in general, some graph families make the problem tractable, while others remain hard even under strong restrictions.
The project combines **theoretical complexity analysis** and **empirical timing experiments**.

---

##  Goals

1. Demonstrate the **boundary between easy and hard graph classes** for Hamiltonian Cycle.
2. Show that certain constraints (e.g., bounded treewidth, low degree) make the problem polynomial-time solvable.
3. Visualize runtime growth empirically for multiple graph families.

---

##  Graph Families Studied

| Category   | Graph Type                    | Theoretical Complexity           |
| ---------- | ----------------------------- | -------------------------------- |
| **Easier** | Degree ≤ 2                    | P (linear-time structural check) |
|            | Tournaments                   | P (Camion’s Theorem — SCC test)  |
|            | Bounded Treewidth             | FPT — (T(n)=O(f(tw)\cdot n))     |
| **Harder** | Bipartite                     | NP-Complete                      |
|            | Planar                        | NP-Complete                      |
|            | Planar + Bipartite + Subcubic | NP-Complete                      |

---

##  Implementation

### Requirements

Install dependencies:

```bash
pip install networkx matplotlib
```

### Run the benchmark

```bash
python benchmark_driver.py
```

This script:

1. Generates random graphs for each class (NetworkX).
2. Runs the appropriate Hamiltonian-cycle solver:

   * Linear-time checks for easy cases.
   * Subset-DP (Held–Karp) for exponential ones.
3. Measures runtime across sizes and saves results.

Output folders:

```
benchmarks/
 ├─ benchmark_results.csv        # timing data
 └─ plots/
     ├─ deg_le2_time.png
     ├─ tournaments_time.png
     ├─ lowtw_time_vs_n.png
     ├─ bipartite_time.png
     ├─ planar_time.png
     ├─ pbs_time.png
     ├─ lowtw_time_vs_k_fixed_n.png
     └─ lowtw_time_vs_n_fixed_k.png
```

---

##  Plots Explained

| Plot                          | Description                                | Growth Trend      |
| ----------------------------- | ------------------------------------------ | ----------------- |
| `deg_le2_time.png`            | Linear-time check — single cycle detection | Flat              |
| `tournaments_time.png`        | Strong-connectivity test (Camion)          | Flat              |
| `lowtw_time_vs_n.png`         | FPT DP, treewidth≈√n                       | Mild              |
| `bipartite_time.png`          | Exponential DP runtime                     | Steep             |
| `planar_time.png`             | NP-hard, exponential                       | Steep             |
| `pbs_time.png`                | NP-hard even with strong limits            | Steep             |
| `lowtw_time_vs_k_fixed_n.png` | Fixed n, vary treewidth                    | Exponential in tw |
| `lowtw_time_vs_n_fixed_k.png` | Fixed tw, vary n                           | Linear in n       |

---

##  Interpretation

* **Low-degree, dense, or tree-like** structures simplify Hamiltonicity.
* **Combinatorially rich** structures (planar, bipartite) preserve NP-hardness.
* The **plots visualize the theory**: easy families show linear-time behavior, while NP-complete ones exhibit exponential growth.

---
#   h a m i l t o n e a n _ c y c l e s  
 