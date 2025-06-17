#!/usr/bin/env python3
"""demo.py – Demonstração dos algoritmos de grafos

Execute:
    python demo.py

O script cria dois grafos relativamente maiores, exibe suas representações
(lista de adjacência) e aplica as operações de união, intersecção, diferença
simétrica, além de verificar propriedades Eulerianas e Hamiltonianas.
"""
from __future__ import annotations

from textwrap import indent

from graph import Graph


# ---------------------------------------------------------------------
#  Definição dos grafos de exemplo                                      
# ---------------------------------------------------------------------
# G₁ – hexágono A-B-C-D-E-F-A com uma corda C-F
G1_adj = {
    "A": ["B", "F"],
    "B": ["A", "C"],
    "C": ["B", "D", "F"],
    "D": ["C", "E"],
    "E": ["D", "F"],
    "F": ["E", "A", "C"],
}
G1 = Graph.from_adjacency_list(G1_adj)

# G₂ – losango C-G-E-F-C com diagonais C-F e G-H-F
G2_adj = {
    "C": ["F", "G"],
    "F": ["C", "E", "H"],
    "E": ["F", "G"],
    "G": ["C", "E", "H"],
    "H": ["F", "G"],
}
G2 = Graph.from_adjacency_list(G2_adj)


# ---------------------------------------------------------------------
#  Utilitários de impressão                                             
# ---------------------------------------------------------------------

# Diagramas ASCII (meramente ilustrativos)
ASCII_G1 = r"""
        A-----B
       /       \
      F---------C
       \       / 
        E-----D
"""

ASCII_G2 = r"""
           G
          / \
         C---E
          \ /
           F
           |
           H
"""

def print_graph(title: str, g: Graph, ascii_art: str | None = None) -> None:
    print(f"\n=== {title} ===")
    if ascii_art:
        print(ascii_art)
    print(f"|V| = {g.num_vertices()}, |E| = {g.num_edges()}")
    print("Lista de adjacência:")
    for v, neigh in g.adjacency_list().items():
        print(f"  {v}: {', '.join(neigh)}")


def print_result(title: str, g: Graph) -> None:
    print(f"\n--- {title} ---")
    print(f"|V| = {g.num_vertices()}, |E| = {g.num_edges()}")
    print(indent("\n".join(f"{v}: {', '.join(neigh)}" for v, neigh in g.adjacency_list().items()), "  "))


# ---------------------------------------------------------------------
#  Exibição básica                                                      
# ---------------------------------------------------------------------
print_graph("G₁", G1, ASCII_G1)
print_graph("G₂", G2, ASCII_G2)

# ---------------------------------------------------------------------
#  Propriedades individuais                                             
# ---------------------------------------------------------------------
for name, g in [("G₁", G1), ("G₂", G2)]:
    print(f"\nPropriedades de {name}:")
    print("  Euleriano :", "SIM" if g.is_eulerian() else "não")
    print("  Hamilton. :", "SIM" if g.has_hamiltonian_cycle() else "não")

# ---------------------------------------------------------------------
#  Operações entre G₁ e G₂                                              
# ---------------------------------------------------------------------
Gu = G1.union(G2)
Gi = G1.intersection(G2)
Gd = G1.symmetric_difference(G2)

print_result("União  G₁ ∪ G₂", Gu)
print_result("Intersecção  G₁ ∩ G₂", Gi)
print_result("Diferença simétrica  G₁ △ G₂", Gd)

print("\nFIM da demonstração.") 