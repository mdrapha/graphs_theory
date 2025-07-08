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

import copy
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

    def union(self, other: "Graph") -> "Graph":
        """Retorna um *novo* grafo G = self ∪ other (união de vértices e arestas)."""
        V = self.V.union(other.V)
        E = self.E.union(other.E)
        return Graph(vertices=V, edges=E)

    def intersection(self, other: "Graph") -> "Graph":
        """Retorna um *novo* grafo contendo apenas vértices e arestas presentes em ambos."""
        V_common = self.V.intersection(other.V)
        # Mantém somente arestas que aparecem em ambos *e* cujos vértices estão no conjunto comum
        E_common = {e for e in self.E.intersection(other.E) if e[0] in V_common and e[1] in V_common}
        return Graph(vertices=V_common, edges=E_common)

    def symmetric_difference(self, other: "Graph") -> "Graph":
        """Retorna um *novo* grafo com a diferença simétrica (arestas em exatamente um dos grafos)."""
        V = self.V.union(other.V)
        E = self.E.symmetric_difference(other.E)
        # Garante inclusão de vértices incidentes às arestas resultantes
        verts_in_edges = {v for edge in E for v in edge}
        V.update(verts_in_edges)
        return Graph(vertices=V, edges=E)

    # ------------------------------------------------------------------ #
    #  Transformações que removem / fundem elementos                     #
    # ------------------------------------------------------------------ #
    def without_vertex(self, v: Vertex) -> "Graph":
        """Retorna um *novo* grafo sem o vértice *v* (e sem arestas incidentes)."""
        self._ensure_vertex(v)
        V = self.V - {v}
        E = {e for e in self.E if v not in e}
        return Graph(vertices=V, edges=E)

    def without_edge(self, u: Vertex, v: Vertex) -> "Graph":
        """Retorna um *novo* grafo sem a aresta (u, v)."""
        self._ensure_vertex(u)
        self._ensure_vertex(v)
        e = (min(u, v), max(u, v))
        if e not in self.E:
            raise ValueError(f"Aresta {e} não pertence ao grafo.")
        E = self.E - {e}
        return Graph(vertices=set(self.V), edges=E)

    def merge_vertices(self, v1: Vertex, v2: Vertex) -> "Graph":
        """Funde *v1* e *v2* num único vértice (mantém o rótulo de v1)."""
        self._ensure_vertex(v1)
        self._ensure_vertex(v2)
        new_V = self.V - {v2}
        new_edges: Set[Edge] = set()
        for a, b in self.E:
            a_new = v1 if a in {v1, v2} else a
            b_new = v1 if b in {v1, v2} else b
            if a_new == b_new:
                continue  # evita laço
            new_edges.add((min(a_new, b_new), max(a_new, b_new)))
        return Graph(vertices=new_V, edges=new_edges)

    # ------------------------------------------------------------------ #
    #  Conectividade / Euler / Hamilton                                #
    # ------------------------------------------------------------------ #
    def _non_isolated_vertices(self) -> Set[Vertex]:
        """Conjunto de vértices com grau > 0."""
        return {v for v, neigh in self.adj.items() if neigh}

    def is_connected(self) -> bool:
        """Verifica se o grafo é conectado (ignorando vértices isolados)."""
        if not self.V:
            return True
        non_iso = self._non_isolated_vertices()
        if not non_iso:
            return True  # sem arestas → considera conectado
        start = next(iter(non_iso))
        visited: Set[Vertex] = set()
        stack = [start]
        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            stack.extend([w for w in self.adj[u] if w not in visited])
        return visited == non_iso

    def is_eulerian(self) -> bool:
        """Retorna True se o grafo possuir circuito Euleriano."""
        if not self.is_connected():
            return False
        return all(len(self.adj[v]) % 2 == 0 for v in self._non_isolated_vertices())

    def hamiltonian_cycle(self) -> Optional[List[Vertex]]:
        """Tenta encontrar um ciclo Hamiltoniano.  Retorna lista de vértices (com repetição do primeiro no fim) ou None."""
        n = len(self.V)
        if n == 0:
            return []
        start = sorted(self.V)[0]
        path: List[Vertex] = [start]
        visited: Set[Vertex] = {start}

        def backtrack(u: Vertex) -> bool:
            if len(path) == n:
                if start in self.adj[u]:
                    path.append(start)
                    return True
                return False
            for w in sorted(self.adj[u]):
                if w not in visited:
                    visited.add(w)
                    path.append(w)
                    if backtrack(w):
                        return True
                    visited.remove(w)
                    path.pop()
            return False

        if backtrack(start):
            return path
        return None

    def has_hamiltonian_cycle(self) -> bool:
        """Atalho booleano para existência de ciclo Hamiltoniano."""
        return self.hamiltonian_cycle() is not None

    # ------------------------------------------------------------------ #
    #  Árvores                                                           #
    # ------------------------------------------------------------------ #
    
    def is_tree(self) -> bool:
        if not self.V: # Grafo vazio não é árvore
            return False
        
        # Um grafo com n vértices é uma árvore se for conectado e tiver n-1 arestas.
        is_conn = self.is_connected()
        has_correct_edges = self.num_edges() == self.num_vertices() - 1
        
        return is_conn and has_correct_edges

    def find_centers(self) -> List[Vertex]:
        if not self.is_tree():
            raise ValueError("O grafo não é uma árvore. Centros são definidos apenas para árvores.")

        g_copy = copy.deepcopy(self)
        
        n = g_copy.num_vertices()
        if n <= 2:
            return sorted(list(g_copy.V))

        leaves = {v for v in g_copy.V if g_copy.degree(v) == 1}

        while n > 2:
            n -= len(leaves)
            
            # Remove as folhas atuais
            next_leaves = set()
            for leaf in leaves:
                # O único vizinho da folha
                neighbor = g_copy.adj[leaf][0]
                
                # Remove a folha do grafo (e arestas incidentes)
                g_copy = g_copy.without_vertex(leaf)

                # Se o vizinho se tornou uma nova folha, adiciona à lista da próxima iteração
                if g_copy.degree(neighbor) == 1:
                    next_leaves.add(neighbor)
            
            leaves = next_leaves

        return sorted(list(g_copy.V))

    def vertex_eccentricities(self) -> Dict[Vertex, int]:
        """Calcula a excentricidade de cada vértice da árvore."""
        if not self.is_tree():
            raise ValueError("A excentricidade está definida apenas para árvores.")

        def bfs(start: Vertex) -> Dict[Vertex, int]:
            visited = {start}
            queue = [(start, 0)]
            dist = {start: 0}
            while queue:
                u, d = queue.pop(0)
                for v in self.adj[u]:
                    if v not in visited:
                        visited.add(v)
                        dist[v] = d + 1
                        queue.append((v, d + 1))
            return dist

        ecc = {}
        for v in self.V:
            distancias = bfs(v)
            ecc[v] = max(distancias.values())
        return ecc

    def radius(self) -> int:
        """Retorna o raio da árvore: a menor excentricidade entre os vértices."""
        if not self.is_tree():
            raise ValueError("O raio está definido apenas para árvores.")
        
        ecc = self.vertex_eccentricities()
        return min(ecc.values())

    def is_subgraph_tree(self, tree_a1: "Graph") -> bool:
        # Verifica se 'tree_a1' é um subgrafo.
        if not tree_a1.is_tree(): # verificando se é árvore
            return False

        return tree_a1.is_subgraph_of(self) 