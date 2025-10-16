# FPT-style Hamiltonicity on bounded-treewidth bands:
# Exponential in tw (=k), linear in n (=k*L).
#
# This code:
# 1) Implements an exact DP over a *path decomposition* tailored to k×L grid-bands.
# 2) Times the solver while (A) fixing n and varying k, and (B) fixing k and varying n.
# 3) Produces two matplotlib plots demonstrating:
#       - exponential dependence on treewidth k,
#       - linear (or close) dependence on n for fixed k.

import time
from collections import defaultdict
import matplotlib.pyplot as plt
import networkx as nx

# -----------------------------
# Band generator: k x L grid
# -----------------------------
def gen_grid_band_kL(k: int, L: int):
    """Return (G, columns) where columns[j] is the list of node ids in column j.
       Nodes are labeled by (r,c) tuples for clarity.
    """
    G = nx.grid_2d_graph(k, L)
    columns = [[] for _ in range(L)]
    for (r,c) in G.nodes():
        columns[c].append((r,c))
    for j in range(L):
        columns[j].sort()
    return G, columns

# -----------------------------
# Helpers for DP over columns
# -----------------------------
def _edges_within_columns(G, col):
    s = set(col); out = []
    for u in col:
        for v in G[u]:
            if v in s and u < v:
                out.append((u,v))
    return out

def _edges_between(G, left_col, right_col):
    sL, sR = set(left_col), set(right_col)
    out = []
    for u in sL:
        for v in G[u]:
            if v in sR:
                out.append((u,v) if u < v else (v,u))
    return list(set(out))

def _canonicalize_matching(pairs):
    return tuple(sorted(tuple(sorted(p)) for p in pairs))

def _apply_edge_to_state(deg_map, matching, a, b):
    """Try to add edge (a,b) locally, respecting degrees ≤ 2 and path-consistency.
       matching is a set of pairs connecting current 'degree-1' endpoints.
    """
    da, db = deg_map[a], deg_map[b]
    if da == 2 or db == 2:
        return None
    da2, db2 = da+1, db+1
    if da2 > 2 or db2 > 2:
        return None

    new_deg = dict(deg_map); new_deg[a]=da2; new_deg[b]=db2
    match = {}
    for x,y in matching:
        match[x]=y; match[y]=x

    def add_pair(u,v):
        if u in match or v in match:
            return None
        match[u]=v; match[v]=u
        return True

    def remove_endpoint(u):
        if u not in match: return None
        v = match[u]; del match[u]; del match[v]; return v

    trans_a = (da, da2); trans_b = (db, db2)
    if trans_a == (0,1) and trans_b == (0,1):
        if add_pair(a,b) is None: return None
    elif trans_a == (1,2) and trans_b == (0,1):
        pa = remove_endpoint(a); 
        if pa is None: return None
        if pa != b:
            if add_pair(b, pa) is None: return None
    elif trans_a == (0,1) and trans_b == (1,2):
        pb = remove_endpoint(b); 
        if pb is None: return None
        if pb != a:
            if add_pair(a, pb) is None: return None
    elif trans_a == (1,2) and trans_b == (1,2):
        pa = remove_endpoint(a); pb = remove_endpoint(b)
        if pa is None or pb is None: return None
        if not (pa == b and pb == a):
            if add_pair(pa, pb) is None: return None

    new_matching = _canonicalize_matching([(u,v) for u,v in match.items() if u < v])
    return new_deg, new_matching

def _initial_state_for_bag(bag_right):
    return {x:0 for x in bag_right}, tuple()

def _restrict_state_to_boundary(deg_map, matching, boundary_set):
    new_deg = {x: deg_map.get(x, 0) for x in boundary_set}
    filt = []
    for a,b in matching:
        if a in boundary_set and b in boundary_set:
            filt.append((a,b))
    return new_deg, _canonicalize_matching(filt)

# -------------------------------------------
# Exact Hamiltonian-cycle DP for k×L bands
# -------------------------------------------
def hc_band_path_dp(G, columns) -> bool:
    """Exact HC decision using a path decomposition over columns.
       Complexity ~ exp(O(k)) * L where k=len(columns[0]).
    """
    L = len(columns)
    if L == 0: return False

    within = [ _edges_within_columns(G, columns[j]) for j in range(L) ]
    between = [ _edges_between(G, columns[j], columns[j+1]) for j in range(L-1) ]

    boundary = set(columns[0])
    init_deg, init_mat = _initial_state_for_bag(boundary)
    cur = { (tuple(sorted(init_deg.items())), init_mat): True }

    for j in range(L):
        left_col = columns[j]
        right_col = columns[j+1] if j+1 < L else []

        nxt = defaultdict(bool)
        for (deg_items, mat) in cur.keys():
            deg_map = dict(deg_items); matching = mat
            for v in right_col:
                if v not in deg_map: deg_map[v]=0
            candidate_edges = list(within[j])
            if j < L-1:
                candidate_edges += list(between[j])

            states = { (tuple(sorted(deg_map.items())), matching) }
            for (a,b) in candidate_edges:
                new_states = set()
                for (d_items, m) in states:
                    d_map = dict(d_items)
                    res = _apply_edge_to_state(d_map, m, a, b)
                    if res is not None:
                        d_after, m_after = res
                        new_states.add( (tuple(sorted(d_after.items())), m_after) )
                    new_states.add( (d_items, m) )
                states = new_states

            for (d_items, m) in states:
                d_map = dict(d_items)
                if all(d_map.get(v,0)==2 for v in left_col):
                    d2, m2 = _restrict_state_to_boundary(d_map, m, set(right_col))
                    nxt[(tuple(sorted(d2.items())), m2)] = True

        cur = nxt
        if not cur:
            return False

    for (deg_items, mat) in cur.keys():
        if len(deg_items)==0 and mat == tuple():
            return True
    return False

# -------------------------------------------
# Timing experiments for the slide
# -------------------------------------------

def plot_fixed_n_vary_k(n0=840, k_values=[2,3,4,5,6,7], out_path="./fpt_fixed_n_vary_k.png"):
    xs=[]; ys=[]
    for k in k_values:
        print("Testing k=",k," n0=",n0)
        if n0 % k != 0:
            continue
        L = n0 // k
        G, cols = gen_grid_band_kL(k, L)
        print("  actual n=",G.number_of_nodes())
        t0=time.perf_counter(); _ = hc_band_path_dp(G, cols); dt=time.perf_counter()-t0
        xs.append(k); ys.append(dt*1000.0)
    plt.figure(figsize=(6,3.8))
    plt.plot(xs, ys, marker='o')
    plt.title("Low-treewidth bands: fixed n, vary tw (k)")
    plt.xlabel("treewidth proxy k (band height)")
    plt.ylabel("time (ms)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path

def plot_fixed_k_vary_n(k0=4, L_values=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50], out_path="./fpt_fixed_k_vary_n.png"):
    xs=[]; ys=[]
    for L in L_values:
        print("Testing k=",k0," L=",L)
        G, cols = gen_grid_band_kL(k0, L)
        t0=time.perf_counter(); _ = hc_band_path_dp(G, cols); dt=time.perf_counter()-t0
        xs.append(k0*L); ys.append(dt*1000.0)
    plt.figure(figsize=(6,3.8))
    plt.plot(xs, ys, marker='o')
    plt.title("Low-treewidth bands: fixed tw (k), vary n")
    plt.xlabel("n = k·L")
    plt.ylabel("time (ms)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path

p1 = plot_fixed_n_vary_k( out_path="./fpt_fixed_n_vary_k.png")
p2 = plot_fixed_k_vary_n( out_path="./fpt_fixed_k_vary_n.png")

[p1,p2]
