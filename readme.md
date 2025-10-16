
# Parameterized Hamiltonicity — Exploring How Graph Constraints Affect Complexity

**Author:** Dimitrios Stamatios Bouras  
**Course:** *Theory of Computation*, Peking University — School of Computer Science  
**Date:** Fall 2025  

---

##  Overview

This project studies how **structural constraints on graphs** affect the difficulty of finding a **Hamiltonian Cycle (HC)**.  
It builds upon the theoretical foundation presented in *“Undirected Hamiltonian Cycle is NP-Complete: Why the Middle Vertex Enforces Direction”* and extends it with **empirical analysis**.

While Hamiltonicity is NP-complete in general, some graph families make the problem **tractable**, while others remain **NP-hard** even under heavy restrictions.  
The project combines **theoretical complexity proofs** and **Python-based experiments**.

---

##  Goals

1. Demonstrate the **boundary between easy and hard graph classes** for Hamiltonian Cycle.  
2. Show that certain constraints (e.g., bounded treewidth, low degree) make the problem polynomial-time solvable.  
3. Visualize how runtime scales with graph size and structural parameters.

---

##  Graph Families Studied

| Category   | Graph Type                    | Theoretical Complexity           |
|-------------|-------------------------------|----------------------------------|
| **Easier**  | Degree ≤ 2                    | P (linear-time structural check) |
|             | Tournaments                   | P (Camion’s Theorem — SCC test)  |
|             | Bounded Treewidth             | FPT — \(T(n)=O(f(tw)\cdot n)\)   |
| **Harder**  | Bipartite                     | NP-Complete                      |
|             | Planar                        | NP-Complete                      |
|             | Planar + Bipartite + Subcubic | NP-Complete                      |

---

##  Implementation

### Requirements

```bash
pip install networkx matplotlib
````

### Running the Benchmarks

There are two scripts:

#### 1. `benchmark_driver.py`

Runs experiments for all graph families except treewidth:

```bash
python benchmark_driver.py
```

Generates plots for:

* Degree ≤ 2 graphs
* Tournament graphs
* Bipartite graphs
* Planar graphs
* Planar–Bipartite–Subcubic graphs

#### 2. `tree_width.py`

Runs the specialized **path-decomposition DP** experiment for bounded-treewidth bands:

```bash
python tree_width.py
```

Generates:

* `lowtw_time_vs_k_fixed_n.png` — fixed number of nodes, vary treewidth
* `lowtw_time_vs_n_fixed_k.png` — fixed treewidth, vary number of nodes

---

##  Output Structure

```
benchmarks/
 ├─ benchmark_results.csv        # timing data
 └─ plots/
     ├─ deg_le2_time.png
     ├─ tournaments_time.png
     ├─ bipartite_time.png
     ├─ planar_time.png
     ├─ pbs_time.png
     ├─ lowtw_time_vs_k_fixed_n.png
     └─ lowtw_time_vs_n_fixed_k.png
```

---

##  Plots Explained

| Plot Name                     | Description                                | Growth Trend       |
| ----------------------------- | ------------------------------------------ | ------------------ |
| `deg_le2_time.png`            | Linear-time check — single cycle detection | Flat               |
| `tournaments_time.png`        | Strong-connectivity check (Camion)         | Flat               |
| `bipartite_time.png`          | Exponential DP runtime                     | Steep              |
| `planar_time.png`             | NP-hard exponential behavior               | Steep              |
| `pbs_time.png`                | NP-hard under strong restrictions          | Steep              |
| `lowtw_time_vs_k_fixed_n.png` | Fixed (n), vary treewidth (k)              | Exponential in (k) |
| `lowtw_time_vs_n_fixed_k.png` | Fixed treewidth, vary number of nodes (n)  | Linear in (n)      |

---

##  Interpretation

* **Low-degree or structured** graphs → easy to solve (linear or polynomial time).
* **Banded graphs** → fixed-parameter tractable (FPT) in treewidth.
* **Planar / Bipartite** → still NP-complete, runtime grows exponentially.

The runtime plots make the complexity boundaries visible:
tractable families yield flat or linear curves, while NP-hard ones rise exponentially.

---