# Create a self-contained benchmark driver that:
# - Generates graphs for each class across sizes/parameters
# - Solves Hamiltonian Cycle with class-appropriate solvers
# - Records runtimes to CSV
# - Produces one matplotlib plot per class (and two for low-treewidth bands)
#
# It can be run as a script; here we'll also execute it once to generate outputs.

import time, math, random, csv, os
from collections import deque
from typing import Optional, Tuple, List, Dict
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.ticker import FuncFormatter

# --------------------- Graph Generators ---------------------

def gen_degree_le2(n: int, make_cycle: bool = False, seed: Optional[int] = None) -> nx.Graph:
    G = nx.Graph(); G.add_nodes_from(range(n))
    for i in range(n-1): G.add_edge(i, i+1)
    if make_cycle and n >= 3: G.add_edge(0, n-1)
    return G

def gen_tournament(n: int, p: float = 0.5, seed: Optional[int] = None) -> nx.DiGraph:
    print("Generating tournament graph with n=",n," p=",p)
    rnd = random.Random(seed); T = nx.DiGraph(); T.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i+1, n):
            if rnd.random() < p: T.add_edge(i, j)
            else: T.add_edge(j, i)
    return T

def gen_low_treewidth_grid(n: int) -> nx.Graph:
    k = max(2, int(round(math.sqrt(max(n, 2)))))
    G = nx.grid_2d_graph(k, k)
    H = nx.convert_node_labels_to_integers(G)
    if H.number_of_nodes() > n:
        nodes = list(range(n)); H = H.subgraph(nodes).copy()
    return H

def gen_grid_band(k: int, L: int) -> nx.Graph:
    G = nx.grid_2d_graph(k, L)  # treewidth ~ k (for k<=L)
    return nx.convert_node_labels_to_integers(G)

def gen_bipartite(n: int, p: float = 0.35, balance: float = 0.5, seed: Optional[int] = None) -> nx.Graph:
    rnd = random.Random(seed)
    n1 = max(1, min(n-1, int(n*balance))); n2 = n - n1
    U = list(range(n1)); V = list(range(n1, n))
    G = nx.Graph(); G.add_nodes_from(range(n))
    for u in U:
        for v in V:
            if rnd.random() < p: G.add_edge(u, v)
    if not nx.is_connected(G) and n1>0 and n2>0:
        m = min(n1, n2)
        for i in range(m):
            G.add_edge(U[i], V[i])
    return G

def gen_planar(n: int, seed: Optional[int] = None, prune_prob: float = 0.05) -> nx.Graph:
    rnd = random.Random(seed)
    k = max(2, int(round(math.sqrt(max(n, 2)))))
    G = nx.grid_2d_graph(k, k)
    if prune_prob > 0:
        for (u, v) in list(G.edges()):
            if rnd.random() < prune_prob: G.remove_edge(u, v)
    H = nx.convert_node_labels_to_integers(G)
    if H.number_of_nodes() > n:
        nodes = list(range(n)); H = H.subgraph(nodes).copy()
    return H

def gen_planar_bipartite_subcubic(n: int, seed: Optional[int] = None) -> nx.Graph:
    G = gen_planar(n, seed=seed, prune_prob=0.0).copy()
    changed = True
    while changed:
        changed = False
        for u in list(G.nodes()):
            while G.degree(u) > 3:
                v = next(iter(G[u]))
                G.remove_edge(u, v)
                changed = True
    if not nx.is_connected(G) and G.number_of_nodes() > 0:
        comp = max(nx.connected_components(G), key=len)
        G = G.subgraph(comp).copy()
    return nx.convert_node_labels_to_integers(G)

# --------------------- Solvers ---------------------

def is_connected_undirected(G: nx.Graph) -> bool:
    if G.number_of_nodes() == 0: return True
    start = next(iter(G.nodes()))
    seen={start}; dq=deque([start])
    while dq:
        u=dq.popleft()
        for v in G.neighbors(u):
            if v not in seen:
                seen.add(v); dq.append(v)
    return len(seen)==G.number_of_nodes()

def hc_cycle_deg_le2(G: nx.Graph) -> Tuple[bool, Optional[List[int]]]:
    n = G.number_of_nodes()
    if n == 0 or not is_connected_undirected(G): return (False, None)
    for _, d in G.degree():
        if d != 2: return (False, None)
    start = next(iter(G.nodes()))
    cycle=[start]; prev=None; cur=start
    for _ in range(n-1):
        nbrs=list(G.neighbors(cur))
        nxt = nbrs[0] if nbrs[0]!=prev else (nbrs[1] if len(nbrs)>1 else None)
        if nxt is None: return (False, None)
        cycle.append(nxt); prev, cur = cur, nxt
    if cycle[0] in G[cycle[-1]] and len(set(cycle))==n: return (True, cycle)
    return (False, None)

def strongly_connected_digraph(T: nx.DiGraph) -> bool:
    if T.number_of_nodes() == 0: return True
    start = next(iter(T.nodes()))
    seen=set(); dq=deque([start])
    while dq:
        u=dq.popleft()
        if u in seen: continue
        seen.add(u)
        for v in T.successors(u):
            if v not in seen: dq.append(v)
    if len(seen)!=T.number_of_nodes(): return False
    seen=set(); dq=deque([start])
    while dq:
        u=dq.popleft()
        if u in seen: continue
        seen.add(u)
        for v in T.predecessors(u):
            if v not in seen: dq.append(v)
    return len(seen)==T.number_of_nodes()

def hc_tournament_exists(T: nx.DiGraph) -> bool:
    return strongly_connected_digraph(T)

def hc_subset_dp_decide(G: nx.Graph) -> bool:
    n = G.number_of_nodes()
    if n == 0 or not is_connected_undirected(G): return False
    nodes=list(G.nodes()); idx={nodes[i]:i for i in range(n)}
    nbr_mask=[0]*n
    for i,u in enumerate(nodes):
        m=0
        for v in G.neighbors(u): m |= (1<<idx[v])
        nbr_mask[i]=m
    r=0; size=1<<n
    print("n=",n," size=",size)
    DP=[0]*size; DP[1<<r]=1<<r
    for S in range(size):
        if not (S & (1<<r)): continue
        reach=DP[S]
        if reach==0: continue
        vb=reach
        while vb:
            v=(vb & -vb).bit_length()-1
            vb &= vb-1
            cand = nbr_mask[v] & (~S)
            while cand:
                w=(cand & -cand).bit_length()-1
                cand &= cand-1
                DP[S | (1<<w)] |= (1<<w)
    full=(1<<n)-1
    endpoints=DP[full]
    if endpoints==0: return False
    while endpoints:
        v=(endpoints & -endpoints).bit_length()-1
        endpoints &= endpoints-1
        if nbr_mask[v] & (1<<0): return True
    return False

# --------------------- Benchmark Runner ---------------------

def avg_runtime(fn, make_graph, sizes, trials=3, **gkw):
    xs=[]; ys=[]
    for n in sizes:
        ts=[]
        for _ in range(trials):
            G = make_graph(n, **gkw)
            t0=time.perf_counter(); _=fn(G); dt=time.perf_counter()-t0
            ts.append(dt)
        xs.append(n); ys.append(sum(ts)/len(ts))
    return xs, ys

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def save_plot(xs, ys, title, xlabel, ylabel, path):
    # convert seconds to milliseconds for plotting
    ys_ms = [y * 1000.0 for y in ys]
    if '(s)' in ylabel:
        ylabel_ms = ylabel.replace('(s)', '(ms)')
    else:
        ylabel_ms = ylabel + ' (ms)'

    plt.figure(figsize=(5.0, 3.2))
    plt.plot(xs, ys_ms, marker='o')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel_ms)
    plt.grid(True, alpha=0.3)

    # nicer formatting for y-axis ticks
    def _fmt(val, pos):
        return f"{val:.1f}" if abs(val) < 10 else f"{val:.0f}"
    plt.gca().yaxis.set_major_formatter(FuncFormatter(_fmt))

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

def save_csv(rows: List[Dict], path: str):
    if not rows: return
    keys = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows: w.writerow(r)

def run_benchmarks():
    out_dir = "./benchmarks"
    plot_dir = os.path.join(out_dir, "plots")
    ensure_dir(plot_dir)

    rows = []

    # 1) Degree ≤ 2
    # sizes_deg2 = [200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000]
    # x,y = avg_runtime(lambda G: hc_cycle_deg_le2(G)[0],
    #                   lambda n, **k: gen_degree_le2(n, make_cycle=True),
    #                   sizes_deg2, trials=3)
    # save_plot(x,y,"Degree ≤ 2","n","time (s)", os.path.join(plot_dir,"deg_le2_time.png"))
    # for n, t in zip(x, y): rows.append({"class":"deg_le2","n":n,"param":"","time":t})

    # 2) Tournaments
    sizes_tourn = [200, 300, 400, 500, 600,700, 800, 900,1000,1100, 1200, 1300, 1400, 1500,1600, 1700, 1800,1900, 2000]
    x,y = avg_runtime(hc_tournament_exists,
                      lambda n, **k: gen_tournament(n, p=0.5),
                      sizes_tourn, trials=3)
    save_plot(x,y,"Tournaments (SCC test)","n","time (s)", os.path.join(plot_dir,"tournaments_time.png"))
    for n, t in zip(x, y): rows.append({"class":"tournament","n":n,"param":"","time":t})

    # # 3) Low-treewidth grids (subset-DP, small n)
    # sizes_lowtw = [8, 10, 12, 14, 16, 18, 20, 22, 24]
    # x,y = avg_runtime(hc_subset_dp_decide,
    #                   lambda n, **k: gen_low_treewidth_grid(n),
    #                   sizes_lowtw, trials=2)
    # save_plot(x,y,"Low-treewidth grids (subset-DP)","n","time (s)", os.path.join(plot_dir,"lowtw_time_vs_n.png"))
    # for n, t in zip(x, y): rows.append({"class":"low_treewidth_grid","n":n,"param":"","time":t})

    # 4) Bipartite (subset-DP)
    # sizes_bip = [8,10, 12, 14, 16, 18, 20,22,24]
    # x,y = avg_runtime(hc_subset_dp_decide,
    #                   lambda n, **k: gen_bipartite(n, p=0.35),
    #                   sizes_bip, trials=2)
    # save_plot(x,y,"Bipartite (subset-DP)","n","time (s)", os.path.join(plot_dir,"bipartite_time.png"))
    # for n, t in zip(x, y): rows.append({"class":"bipartite","n":n,"param":"","time":t})

    # # 5) Planar (subset-DP)
    # sizes_plan = [8,10, 12, 14, 16, 18, 20,22,24]
    # x,y = avg_runtime(hc_subset_dp_decide,
    #                   lambda n, **k: gen_planar(n, prune_prob=0.05),
    #                   sizes_plan, trials=2)
    # save_plot(x,y,"Planar (subset-DP)","n","time (s)", os.path.join(plot_dir,"planar_time.png"))
    # for n, t in zip(x, y): rows.append({"class":"planar","n":n,"param":"","time":t})

    # # 6) Planar + bipartite + subcubic (subset-DP)
    # sizes_pbs = [8,10, 12, 14, 16, 18, 20,22,24]
    # x,y = avg_runtime(hc_subset_dp_decide,
    #                   lambda n, **k: gen_planar_bipartite_subcubic(n),
    #                   sizes_pbs, trials=2)
    # save_plot(x,y,"Planar+Bipartite+Subcubic (subset-DP)","n","time (s)", os.path.join(plot_dir,"pbs_time.png"))
    # for n, t in zip(x, y): rows.append({"class":"planar_bipartite_subcubic","n":n,"param":"","time":t})

    # # Low-treewidth specials
    # # A) Fixed n0, vary k
    # n0 = 18; k_values = [2,3,4,5,6,7,8,9,10]; xs=[]; ys=[]
    # for k in k_values:
    #     L = max(2, n0 // k)
    #     G = gen_grid_band(k, L)
    #     t0=time.perf_counter(); _=hc_subset_dp_decide(G); dt=time.perf_counter()-t0
    #     xs.append(k); ys.append(dt)
    #     rows.append({"class":"low_tw_band","n":G.number_of_nodes(),"param":f"k={k}", "time":dt})
    # save_plot(xs, ys, "Low-treewidth bands: fixed n, vary k", "band height k (tw proxy)", "time (s)",
    #           os.path.join(plot_dir,"lowtw_time_vs_k_fixed_n.png"))

    # # B) Fixed k0, vary n by changing L
    # k0 = 3; L_values = [3,4,5,6,7,8]; xs=[]; ys=[]
    # for L in L_values:
    #     G = gen_grid_band(k0, L); n = G.number_of_nodes()
    #     print("Testing low-treewidth band with k=",k0," L=",L," n=",n)
    #     t0=time.perf_counter(); _=hc_subset_dp_decide(G); dt=time.perf_counter()-t0
    #     xs.append(n); ys.append(dt)
    #     rows.append({"class":"low_tw_band","n":n,"param":f"k={k0}", "time":dt})
    # save_plot(xs, ys, "Low-treewidth bands: fixed k, vary n", "n = k·L", "time (s)",
    #           os.path.join(plot_dir,"lowtw_time_vs_n_fixed_k.png"))

    # Save CSV of all rows
    csv_path = os.path.join(out_dir, "benchmark_results.csv")
    save_csv(rows, csv_path)
    return out_dir, plot_dir, csv_path

# Execute once now
out_dir, plot_dir, csv_path = run_benchmarks()
out_dir, plot_dir, csv_path
('./benchmarks',
 './benchmarks/plots',
 './benchmarks/benchmark_results.csv')