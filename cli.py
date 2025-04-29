#!/usr/bin/env python3
"""
cli.py – Interface em modo texto para o pacote de grafos
=======================================================

Modos de uso
------------

1. **Menu interativo**      →  `python cli.py`
2. **Testes rápidos embutidos** →  `python cli.py --test`
"""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional, Set, Tuple

from graph import Graph, Vertex, Edge

# --------------------------------------------------------------------- #
#  Banner                                                              #
# --------------------------------------------------------------------- #
def print_banner() -> None:
    print(r"""
================================================================================
   ____ ___  _   _ _____ _   _ _____ ___ ____   ___  ____   ____  ____  _____ 
  / ___/ _ \| \ | |_   _| | | | ____/ _ \___ \ / _ \|  _ \ / ___||  _ \| ____|
 | |  | | | |  \| | | | | |_| |  _|| | | |__) | | | | |_) | |  _ | |_) |  _|  
 | |__| |_| | |\  | | | |  _  | |__| |_| / __/ | |_| |  _ <| |_| ||  _ <| |___ 
  \____\___/|_| \_| |_| |_| |_|_____\___/_____| \___/|_| \_\\____||_| \_\_____|
                          (Disciplina: Teoria de Grafos)
================================================================================
""")


# --------------------------------------------------------------------- #
#  Ajuda / Tutorial                                                     #
# --------------------------------------------------------------------- #
def print_help() -> None:
    print(
        """
Ajuda / Tutorial
----------------
0. Sair
1. Carregar ou recriar grafo
2. Exibir representações (matriz adj., incidência, lista)
3. Métricas básicas (|V|, |E|, graus)
4. Consultas (vizinhos, aresta, caminho, ciclo)
5. Verificar subgrafo
6. Ajuda / Tutorial

Dentro da opção 1 você escolhe o formato de entrada:
  • 1 → lista de arestas  (ex.:  A B [Enter] B C … [vazio p/ terminar])
  • 2 → matriz de adjacência
  • 3 → matriz de incidência
Digite **h** para exibir exemplos durante a digitação.
"""
    )


def print_format_examples() -> None:
    print(
        """
Exemplos de entrada de grafos
-----------------------------
1) Lista de arestas
   Digite pares separados por espaço, um por linha.  Exemplo:
       A B
       A C
       B D
       (linha vazia para terminar)

2) Matriz de adjacência (n × n)
   Primeiro informe n.  Depois escreva cada linha da matriz:
       0 1 1 0
       1 0 0 1
       1 0 0 0
       0 1 0 0

3) Matriz de incidência (n × m)
   n vértices, m arestas.  Cada coluna tem dois 1s:
       1 1 0
       1 0 1
       0 0 1
       0 1 0
"""
    )


# --------------------------------------------------------------------- #
#  Funções de prompt de entrada                                         #
# --------------------------------------------------------------------- #
def prompt_edges() -> Set[Edge]:
    print("Digite as arestas (u v), uma por linha. Linha vazia encerra.  (h = ajuda)")
    edges: Set[Edge] = set()
    while True:
        line = input("edge> ").strip()
        if not line:
            break
        if line.lower() in {"h", "help"}:
            print_format_examples()
            continue
        u, *rest = line.split()
        if len(rest) != 1:
            print("Formato inválido! Digite exatamente dois vértices.")
            continue
        v = rest[0]
        edges.add((min(u, v), max(u, v)))
    return edges


def prompt_vertex(label: str = "vértice") -> Vertex:
    return input(f"{label}> ").strip()


def prompt_matrix(rows: int, cols: int, kind: str) -> List[List[int]]:
    matrix: List[List[int]] = []
    for i in range(rows):
        while True:
            row_str = input(f"{kind} linha {i}> ").strip()
            if row_str.lower() in {"h", "help"}:
                print_format_examples()
                continue
            try:
                row = list(map(int, row_str.split()))
            except ValueError:
                print("Use apenas 0 ou 1, separados por espaço.")
                continue
            if len(row) != cols or any(x not in {0, 1} for x in row):
                print(f"A linha deve ter {cols} valores 0/1.")
                continue
            matrix.append(row)
            break
    return matrix


def load_graph_menu() -> Optional[Graph]:
    while True:
        print(
            """
=== Como deseja construir o grafo? ===
  1. Inserir lista de arestas
  2. Inserir matriz de adjacência
  3. Inserir matriz de incidência
  h. Ajuda sobre formatos de entrada
  0. Cancelar
"""
        )
        choice = input("Escolha: ").strip().lower()

        if choice == "0":
            return None
        if choice == "h":
            print_format_examples()
            continue
        if choice == "1":
            edges = prompt_edges()
            return Graph(edges=edges)

        if choice == "2":
            try:
                n = int(input("Número de vértices n: "))
            except ValueError:
                print("Digite um inteiro válido.")
                continue
            M = prompt_matrix(n, n, "matriz")
            labels = [
                input(f"rótulo do vértice {i} (Enter = {i}): ") or str(i)
                for i in range(n)
            ]
            return Graph.from_adjacency_matrix(M, labels)

        if choice == "3":
            try:
                n = int(input("Número de vértices n: "))
                m = int(input("Número de arestas m: "))
            except ValueError:
                print("Digite valores inteiros válidos.")
                continue
            M = prompt_matrix(n, m, "matriz de incidência")
            labels = [
                input(f"rótulo do vértice {i} (Enter = {i}): ") or str(i)
                for i in range(n)
            ]
            try:
                return Graph.from_incidence_matrix(M, labels)
            except ValueError as e:
                print(f"Erro: {e}")
                continue

        print("Opção inválida! Tente novamente.")


# --------------------------------------------------------------------- #
#  Loop principal                                                       #
# --------------------------------------------------------------------- #
def interactive_menu() -> None:
    graph: Optional[Graph] = None
    print_banner()

    while True:
        print(
            """
====================  MENU PRINCIPAL  ====================
1  Carregar / recriar grafo
2  Exibir representações
3  Métricas básicas
4  Consultas
5  Verificar subgrafo
6  Ajuda / Tutorial
0  Sair
==========================================================
"""
        )
        cmd = input("Escolha uma opção: ").strip()

        if cmd == "0":
            print("Até logo!")
            break

        if cmd == "6":
            print_help()
            continue

        if cmd == "1":
            g = load_graph_menu()
            if g:
                graph = g
                print("Grafo carregado com sucesso!")
            continue

        if graph is None:
            print("Nenhum grafo carregado. Use a opção 1 primeiro.")
            continue

        if cmd == "2":
            print("\n--- Matriz de adjacência ---")
            for row in graph.adjacency_matrix():
                print(" ".join(map(str, row)))
            print("\n--- Matriz de incidência ---")
            inc = graph.incidence_matrix()
            for row in inc:
                print(" ".join(map(str, row)))
            print("\n--- Lista de adjacência ---")
            for v, neigh in graph.adjacency_list().items():
                print(f"{v}: {', '.join(neigh)}")

        elif cmd == "3":
            print(f"|V| = {graph.num_vertices()}")
            print(f"|E| = {graph.num_edges()}")
            print("Graus:")
            for v, d in graph.degrees().items():
                print(f"  {v}: {d}")

        elif cmd == "4":
            print(
                """
--- Consultas ---
a) Vizinhos de um vértice
b) Verificar aresta entre dois vértices
c) Caminho simples entre dois vértices
d) Ciclo que contém um vértice
"""
            )
            sub = input("Escolha: ").strip().lower()
            if sub == "a":
                v = prompt_vertex()
                print("Adjacentes:", graph.neighbors(v))
            elif sub == "b":
                u = prompt_vertex("u")
                v = prompt_vertex("v")
                print("Existe aresta?", graph.are_adjacent(u, v))
            elif sub == "c":
                u = prompt_vertex("origem")
                v = prompt_vertex("destino")
                path = graph.simple_path(u, v)
                print("Caminho:", path or "Nenhum caminho.")
            elif sub == "d":
                v = prompt_vertex()
                cycle = graph.cycle_containing(v)
                print("Ciclo:", cycle or "Nenhum ciclo encontrado.")
            else:
                print("Opção inválida.")

        elif cmd == "5":
            print("Insira o grafo para comparar (será testado como subgrafo).")
            other = load_graph_menu()
            if other:
                if other.is_subgraph_of(graph):
                    print("O grafo inserido é SUBGRAFO de G.")
                elif graph.is_subgraph_of(other):
                    print("G é SUBGRAFO do grafo inserido.")
                else:
                    print("Nenhum é subgrafo do outro.")
        else:
            print("Comando desconhecido!")

        print("\n")  # separador visual


# --------------------------------------------------------------------- #
#  Testes rápidos embutidos                                             #
# --------------------------------------------------------------------- #
def run_tests() -> None:
    print("Rodando testes unitários rápidos...")

    # Grafo quadrado A-B-D-C
    g = Graph()
    for u, v in ("A B", "B D", "D C", "C A"):
        u, v = u.split()
        g.add_edge(u, v)

    assert g.num_vertices() == 4
    assert g.num_edges() == 4
    assert g.degree("A") == 2
    assert g.are_adjacent("A", "B") is True
    assert g.are_adjacent("A", "D") is False

    # Conversões
    M_adj = g.adjacency_matrix()
    g2 = Graph.from_adjacency_matrix(M_adj, sorted(g.V))
    assert g2.E == g.E

    M_inc = g.incidence_matrix()
    g3 = Graph.from_incidence_matrix(M_inc, sorted(g.V))
    assert g3.E == g.E

    # Caminho simples
    path = g.simple_path("A", "D")
    assert path in (["A", "B", "D"], ["A", "C", "D"])

    # Ciclo
    cycle = g.cycle_containing("A")
    assert cycle is not None and len(cycle) == 4

    # Subgrafo
    g_sub = Graph(edges={("A", "B"), ("B", "D")})
    assert g_sub.is_subgraph_of(g) is True
    assert g.is_subgraph_of(g_sub) is False

    print("🎉  All tests passed!")


# --------------------------------------------------------------------- #
#  Entry-point                                                          #
# --------------------------------------------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser(description="CLI de grafos.")
    parser.add_argument(
        "-t", "--test", action="store_true", help="Executa testes rápidos e sai."
    )
    args = parser.parse_args()

    if args.test:
        run_tests()
    else:
        interactive_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nInterrompido pelo usuário.")