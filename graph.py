#!/usr/bin/env python3
"""
graph.py – Núcleo de estruturas e algoritmos de grafos
=====================================================

Implementa, **do zero**, todas as rotinas exigidas nos Exercícios 1 & 2
da Série 3 (Introdução à Teoria de Grafos).  Nenhuma biblioteca externa
de grafos é usada.

Exporta:
    • Vertex – alias para str
    • Edge   – Tuple[Vertex, Vertex]
    • Graph  – classe principal
"""
from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

__all__ = ["Vertex", "Edge", "Graph"]

Vertex = str
Edge = Tuple[Vertex, Vertex]


class Graph:
    """Grafo simples, não direcionado, sem laços nem paralelas."""

    # ------------------------------------------------------------------ #
    # Construção                                                         #
    # ------------------------------------------------------------------ #
    def __init__(
        self,
        vertices: Optional[Set[Vertex]] = None,
        edges: Optional[Set[Edge]] = None,
    ) -> None:
        self.V: Set[Vertex] = set(vertices) if vertices else set()
        self.E: Set[Edge] = set()
        self.adj: Dict[Vertex, List[Vertex]] = {v: [] for v in self.V}

        if edges:
            for u, v in edges:
                self.add_edge(u, v)

    def add_vertex(self, v: Vertex) -> None:
        if v not in self.V:
            self.V.add(v)
            self.adj[v] = []

    def add_edge(self, u: Vertex, v: Vertex) -> None:
        if u == v:
            raise ValueError("Laços não são permitidos em grafos simples (u == v).")
        self.add_vertex(u)
        self.add_vertex(v)
        e = (min(u, v), max(u, v))  # representação canônica
        if e not in self.E:
            self.E.add(e)
            self.adj[u].append(v)
            self.adj[v].append(u)

    # ------------------------------------------------------------------ #
    # Conversões de representação                                        #
    # ------------------------------------------------------------------ #
    def adjacency_matrix(self) -> List[List[int]]:
        index = {v: i for i, v in enumerate(sorted(self.V))}
        n = len(self.V)
        M = [[0] * n for _ in range(n)]
        for u, v in self.E:
            i, j = index[u], index[v]
            M[i][j] = M[j][i] = 1
        return M

    @classmethod
    def from_adjacency_matrix(
        cls, M: List[List[int]], labels: Optional[List[Vertex]] = None
    ) -> "Graph":
        n = len(M)
        if labels is None:
            labels = [str(i) for i in range(n)]
        if len(labels) != n:
            raise ValueError("Número de rótulos deve coincidir com tamanho da matriz.")
        g = cls()
        for i in range(n):
            for j in range(i + 1, n):
                if M[i][j]:
                    g.add_edge(labels[i], labels[j])
        return g

    def incidence_matrix(self) -> List[List[int]]:
        V_sorted = sorted(self.V)
        E_sorted = sorted(self.E)
        idx_v = {v: i for i, v in enumerate(V_sorted)}
        M = [[0] * len(E_sorted) for _ in range(len(V_sorted))]
        for e_idx, (u, v) in enumerate(E_sorted):
            M[idx_v[u]][e_idx] = 1
            M[idx_v[v]][e_idx] = 1
        return M

    @classmethod
    def from_incidence_matrix(
        cls, M: List[List[int]], labels: Optional[List[Vertex]] = None
    ) -> "Graph":
        n = len(M)
        m = len(M[0]) if n else 0
        if labels is None:
            labels = [str(i) for i in range(n)]
        g = cls()
        for e in range(m):
            verts = [labels[v] for v in range(n) if M[v][e] == 1]
            if len(verts) != 2:
                raise ValueError("Matriz de incidência inválida para grafo simples.")
            g.add_edge(verts[0], verts[1])
        return g

    def adjacency_list(self) -> Dict[Vertex, List[Vertex]]:
        return {v: sorted(neigh) for v, neigh in self.adj.items()}

    @classmethod
    def from_adjacency_list(cls, L: Dict[Vertex, List[Vertex]]) -> "Graph":
        g = cls()
        for u, neighs in L.items():
            for v in neighs:
                g.add_edge(u, v)
        return g

    # ------------------------------------------------------------------ #
    # Métricas e consultas básicas                                       #
    # ------------------------------------------------------------------ #
    def num_vertices(self) -> int:
        return len(self.V)

    def num_edges(self) -> int:
        return len(self.E)

    def neighbors(self, v: Vertex) -> List[Vertex]:
        self._ensure_vertex(v)
        return sorted(self.adj[v])

    def are_adjacent(self, u: Vertex, v: Vertex) -> bool:
        self._ensure_vertex(u)
        self._ensure_vertex(v)
        return v in self.adj[u]

    def degree(self, v: Vertex) -> int:
        self._ensure_vertex(v)
        return len(self.adj[v])

    def degrees(self) -> Dict[Vertex, int]:
        return {v: len(neigh) for v, neigh in self.adj.items()}

    # ------------------------------------------------------------------ #
    # Caminho simples (DFS)                                              #
    # ------------------------------------------------------------------ #
    def simple_path(self, start: Vertex, goal: Vertex) -> Optional[List[Vertex]]:
        self._ensure_vertex(start)
        self._ensure_vertex(goal)
        visited: Set[Vertex] = set()
        path: List[Vertex] = []

        def dfs(u: Vertex) -> bool:
            visited.add(u)
            path.append(u)
            if u == goal:
                return True
            for w in self.adj[u]:
                if w not in visited and dfs(w):
                    return True
            path.pop()
            return False

        if dfs(start):
            return path
        return None

    # ------------------------------------------------------------------ #
    # Ciclo contendo um vértice (DFS)                                    #
    # ------------------------------------------------------------------ #
    def cycle_containing(self, v: Vertex) -> Optional[List[Vertex]]:
        self._ensure_vertex(v)
        parent: Dict[Vertex, Vertex] = {}
        visited: Set[Vertex] = set()

        def dfs(u: Vertex, p: Optional[Vertex]) -> Optional[List[Vertex]]:
            visited.add(u)
            for w in self.adj[u]:
                if w == p:
                    continue
                if w in visited:
                    # monta ciclo
                    cycle = [w, u]
                    x = u
                    while x != w:
                        x = parent[x]
                        cycle.append(x)
                    cycle.reverse()
                    return cycle
                parent[w] = u
                c = dfs(w, u)
                if c:
                    return c
            return None

        return dfs(v, None)

    # ------------------------------------------------------------------ #
    # Subgrafo                                                           #
    # ------------------------------------------------------------------ #
    def is_subgraph_of(self, other: "Graph") -> bool:
        return self.V.issubset(other.V) and self.E.issubset(other.E)

    # ------------------------------------------------------------------ #
    # Helpers e representações                                           #
    # ------------------------------------------------------------------ #
    def _ensure_vertex(self, v: Vertex) -> None:
        if v not in self.V:
            raise ValueError(f"Vértice '{v}' não pertence ao grafo.")

    def __str__(self) -> str:  # pragma: no cover
        return f"Graph(V={sorted(self.V)}, E={sorted(self.E)})"

    __repr__ = __str__