"""tests/test_new_methods.py – Exemplos de teste dos métodos recém-implementados.

Para executar:
    pytest -q tests/test_new_methods.py
"""

from graph import Graph


# --------------------------------------------------------------------
#  Helpers
# --------------------------------------------------------------------

# Helper para construir grafo a partir de dict de adjacência
def G(adj: dict[str, list[str]]) -> Graph:  # noqa: N802
    return Graph.from_adjacency_list(adj)


def square_graph() -> Graph:
    """Quadrado A-B-D-C representado por lista de adjacência."""
    adj = {
        "A": ["B", "C"],
        "B": ["A", "D"],
        "C": ["A", "D"],
        "D": ["B", "C"],
    }
    return G(adj)


def path_graph() -> Graph:
    """Caminho simples A-B-C-D representado por lista de adjacência (não Hamiltoniano)."""
    adj = {
        "A": ["B"],
        "B": ["A", "C"],
        "C": ["B", "D"],
        "D": ["C"],
    }
    return G(adj)


# --------------------------------------------------------------------
#  Operações de conjunto (união / intersecção / diferença simétrica)
# --------------------------------------------------------------------

def test_union_and_symmetric_difference():
    g1 = G({"A": ["B"], "B": ["A", "C"]})
    g2 = G({"B": ["C"], "C": ["B", "D"]})

    u = g1.union(g2)
    assert u.E == {("A", "B"), ("B", "C"), ("C", "D")}
    assert u.V == {"A", "B", "C", "D"}

    sd = g1.symmetric_difference(g2)
    # Apenas arestas exclusivas
    assert sd.E == {("A", "B"), ("C", "D")}


# --------------------------------------------------------------------
#  Remoção de vértice / aresta
# --------------------------------------------------------------------

def test_without_vertex_and_edge():
    g = square_graph()  # 4 vértices, 4 arestas
    g2 = g.without_vertex("A")
    assert "A" not in g2.V
    # Arestas incidentes a A removidas
    assert all("A" not in e for e in g2.E)

    g3 = g.without_edge("A", "B")
    assert ("A", "B") not in g3.E and ("B", "A") not in g3.E
    # Demais arestas permanecem
    assert len(g3.E) == 3


# --------------------------------------------------------------------
#  Fusão de vértices
# --------------------------------------------------------------------

def test_merge_vertices():
    g = square_graph()
    merged = g.merge_vertices("A", "B")
    # Número de vértices cai de 4 para 3
    assert merged.num_vertices() == 3
    # Não deve haver laço nem múltiplas paralelas
    assert all(a != b for a, b in merged.E)


# --------------------------------------------------------------------
#  Conectividade / Euler / Hamilton
# --------------------------------------------------------------------

def test_is_connected():
    g = G({"A": ["B"], "B": ["A"], "C": ["D"], "D": ["C"]})  # dois componentes
    assert g.is_connected() is False
    g2 = G({"A": ["B"], "B": ["A", "C"]})
    assert g2.is_connected() is True


def test_is_eulerian():
    g = square_graph()  # todos graus 2 -> Euleriano
    assert g.is_eulerian() is True
    g2 = path_graph()  # dois vértices de grau ímpar -> não Euleriano
    assert g2.is_eulerian() is False


def test_hamiltonian_cycle_presence():
    g1 = square_graph()
    assert g1.has_hamiltonian_cycle() is True
    g2 = path_graph()
    assert g2.has_hamiltonian_cycle() is False 