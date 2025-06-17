#!/usr/bin/env python3
"""
tests/test_graph.py  –  suíte pytest para o módulo graph.py
===========================================================

Execute na raiz do projeto:

    pytest                       # roda todos os testes
    pytest -q                    # saída resumida
"""
import pytest  # type: ignore

from graph import Graph


# --------------------------------------------------------------------
#  Fixtures
# --------------------------------------------------------------------
@pytest.fixture
def square_graph() -> Graph:
    """
    Grafo de referência (quadrado A-B-D-C).

        A ----- B
        |       |
        C ----- D
    """
    g = Graph()
    for pair in ("A B", "B D", "D C", "C A"):
        u, v = pair.split()
        g.add_edge(u, v)
    return g


# --------------------------------------------------------------------
#  Testes de construção e conversões
# --------------------------------------------------------------------
def test_add_vertices_edges(square_graph: Graph):
    g = square_graph
    assert g.num_vertices() == 4
    assert g.num_edges() == 4
    assert g.degrees()["A"] == 2


def test_adjacency_matrix_roundtrip(square_graph: Graph):
    g = square_graph
    M = g.adjacency_matrix()
    g2 = Graph.from_adjacency_matrix(M, sorted(g.V))
    assert g2.E == g.E
    assert g2.V == g.V


def test_incidence_matrix_roundtrip(square_graph: Graph):
    g = square_graph
    M = g.incidence_matrix()
    g2 = Graph.from_incidence_matrix(M, sorted(g.V))
    assert g2.E == g.E
    assert g2.V == g.V


def test_adjacency_list_roundtrip(square_graph: Graph):
    g = square_graph
    L = g.adjacency_list()
    g2 = Graph.from_adjacency_list(L)
    assert g2.E == g.E
    assert g2.V == g.V


# --------------------------------------------------------------------
#  Testes de métricas e consultas
# --------------------------------------------------------------------
def test_neighbors_and_adjacency(square_graph: Graph):
    g = square_graph
    assert set(g.neighbors("A")) == {"B", "C"}
    assert g.are_adjacent("A", "B") is True
    assert g.are_adjacent("A", "D") is False


def test_simple_path(square_graph: Graph):
    g = square_graph
    path = g.simple_path("A", "D")
    # Duas rotas possíveis: A-B-D ou A-C-D
    assert path in (["A", "B", "D"], ["A", "C", "D"])


def test_cycle_containing(square_graph: Graph):
    g = square_graph
    cycle = g.cycle_containing("A")
    # O ciclo deve incluir todos os vértices no quadrado
    assert cycle is not None and set(cycle) == {"A", "B", "C", "D"}


def test_degrees(square_graph: Graph):
    g = square_graph
    all_deg_two = all(d == 2 for d in g.degrees().values())
    assert all_deg_two is True


# --------------------------------------------------------------------
#  Testes de subgrafo
# --------------------------------------------------------------------
def test_subgraph(square_graph: Graph):
    g = square_graph
    sub = Graph(edges={("A", "B"), ("B", "D")})
    assert sub.is_subgraph_of(g) is True
    assert g.is_subgraph_of(sub) is False


def test_is_connected_and_eulerian(square_graph: Graph):
    g = square_graph
    assert g.is_connected() is True
    assert g.is_eulerian() is True  # todos os vértices grau 2


def test_intersection(square_graph: Graph):
    g1 = square_graph
    g2 = Graph(edges={("A", "B"), ("B", "D"), ("X", "Y")})
    inter = g1.intersection(g2)
    assert inter.E == {("A", "B"), ("B", "D")}
    # vértices incidentes devem estar presentes
    assert inter.V == {"A", "B", "D"}


def test_hamiltonian_cycle(square_graph: Graph):
    g = square_graph
    cycle = g.hamiltonian_cycle()
    assert cycle is not None
    assert cycle[0] == cycle[-1]  # ciclo fechado
    assert set(cycle[:-1]) == g.V  # cobre todos vértices