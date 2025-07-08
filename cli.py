#!/usr/bin/env python3
"""
cli.py – Interface em modo texto para o pacote de grafos
=======================================================

• Menu interativo ............  python cli.py
• Testes rápidos embutidos ...  python cli.py --test
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import csv_loader  # utilitário para ler CSVs da pasta ./files
from graph import Edge, Graph, Vertex

# ======================================================================#
#  Banner                                                               #
# ======================================================================#


def print_banner() -> None:
    print(
        r"""
================================================================================
   _____ ____  _   _ ______ _____ _______       _____   ____   _____ 
  / ____/ __ \| \ | |  ____/ ____|__   __|/\   |  __ \ / __ \ / ____|
 | |   | |  | |  \| | |__ | |       | |  /  \  | |  | | |  | | (___  
 | |   | |  | | . ` |  __|| |       | | / /\ \ | |  | | |  | |\___ \ 
 | |___| |__| | |\  | |___| |____   | |/ ____ \| |__| | |__| |____) |
  \_____\____/|_| \_|______\_____|  |_/_/    \_\_____/ \____/|_____/ 
                                                                    
                    (Disciplina: Teoria de Grafos)
================================================================================
"""
    )


# ======================================================================#
#  Ajuda / Tutorial                                                     #
# ======================================================================#


def print_help() -> None:
    print(
        """
Ajuda / Tutorial
----------------
0  Sair
1  Carregar ou recriar grafo
2  Exibir representações (matriz, incidência, lista)
3  Operações (|V|, |E|, vizinhos, grau, caminho, ciclo, subgrafo)
4  Ajuda / Tutorial

Dentro da opção 1 você escolhe o formato de entrada:
  • 1 → lista de arestas  (ex.:  A B  ↵  B C …  [linha vazia p/ terminar])
  • 2 → matriz de adjacência
  • 3 → matriz de incidência
  • 4 → CSV da pasta ./files
Digite **h** a qualquer momento para ver exemplos.
"""
    )


def print_format_examples() -> None:
    print(
        """
Exemplos de entrada de grafos
-----------------------------
1) Lista de arestas
   A B
   A C
   B D
   (linha vazia p/ terminar)

2) Matriz de adjacência (4×4)
   0 1 1 0
   1 0 0 1
   1 0 0 0
   0 1 0 0

3) Matriz de incidência (4×3)
   1 1 0
   1 0 1
   0 0 1
   0 1 0

4) Arquivos CSV em ./files
   adj.csv  → matriz de adjacência
   inc.csv  → matriz de incidência
   list.csv → lista de adjacência
"""
    )


# ======================================================================#
#  Funções de prompt                                                    #
# ======================================================================#


def prompt_edges() -> Set[Edge]:
    print("Digite as arestas (u v). Linha vazia encerra.  (h = ajuda)")
    edges: Set[Edge] = set()
    while True:
        line = input("edge> ").strip()
        if not line:
            break
        if line.lower() in {"h", "help"}:
            print_format_examples()
            continue
        parts = line.split()
        if len(parts) != 2:
            print("Digite exatamente dois vértices.")
            continue
        u, v = parts
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
                print("Use apenas 0 ou 1.")
                continue
            if len(row) != cols or any(x not in {0, 1} for x in row):
                print(f"A linha deve ter {cols} valores 0/1.")
                continue
            matrix.append(row)
            break
    return matrix


# ======================================================================#
#  CSV loader helpers                                                   #
# ======================================================================#


def choose_csv_file() -> Optional[str]:
    files = csv_loader.list_csv_files()
    if not files:
        print("Nenhum CSV encontrado em ./files.")
        return None

    print("\nArquivos em ./files:")
    for idx, name in enumerate(files, start=1):
        print(f"{idx:2}) {name}")
    print(" 0) Cancelar")

    while True:
        try:
            num = int(input("Escolha o número do arquivo: "))
        except ValueError:
            print("Digite um número válido.")
            continue
        if num == 0:
            return None
        if 1 <= num <= len(files):
            return files[num - 1]
        print("Número fora da lista.")


def load_graph_from_csv() -> Optional[Graph]:
    fname = choose_csv_file()
    if not fname:
        return None

    fmt = input("Formato deste CSV (adj/inc/list): ").strip().lower()
    try:
        if fmt == "adj":
            M = csv_loader.read_matrix(fname)
            return Graph.from_adjacency_matrix(M, [str(i+1) for i in range(len(M))])
        if fmt == "inc":
            M = csv_loader.read_matrix(fname)
            return Graph.from_incidence_matrix(M, [str(i+1) for i in range(len(M))])
        if fmt == "list":
            return Graph.from_adjacency_list(csv_loader.read_adj_list(fname))
        print("Formato não reconhecido (use adj/inc/list).")
    except Exception as e:
        print(f"Erro ao ler CSV: {e}")
    return None


# ======================================================================#
#  Menu de criação                                                      #
# ======================================================================#


def load_graph_menu() -> Optional[Graph]:
    while True:
        print(
            """
=== Como deseja construir o grafo? ===
  1. Inserir lista de arestas
  2. Inserir matriz de adjacência
  3. Inserir matriz de incidência
  4. Carregar de CSV
  h. Ajuda sobre formatos
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
            return Graph(edges=prompt_edges())
        if choice == "2":
            try:
                n = int(input("Número de vértices n: "))
            except ValueError:
                print("Digite um inteiro válido.")
                continue
            M = prompt_matrix(n, n, "matriz")
            labels = [input(f"rótulo {i+1} (Enter={i+1}): ") or str(i) for i in range(n)]
            return Graph.from_adjacency_matrix(M, labels)
        if choice == "3":
            try:
                n = int(input("Número de vértices n: "))
                m = int(input("Número de arestas m: "))
            except ValueError:
                print("Digite inteiros válidos.")
                continue
            M = prompt_matrix(n, m, "incidência")
            labels = [input(f"rótulo {i+1} (Enter={i+1}): ") or str(i+1) for i in range(n)]
            try:
                return Graph.from_incidence_matrix(M, labels)
            except ValueError as e:
                print(f"Erro: {e}")
                continue
        if choice == "4":
            g = load_graph_from_csv()
            if g:
                return g
            continue

        print("Opção inválida!")


# ======================================================================#
#  Submenu de operações                                                 #
# ======================================================================#


def operations_menu(g: Graph) -> None:
    while True:
        print(
            """
--- OPERACOES ---
1  |V|   – número de vértices
2  |E|   – número de arestas
3  Vizinhos de um vértice
4  Existe aresta entre dois vértices
5  Grau de um vértice
6  Graus de todos os vértices
7  Caminho simples entre dois vértices
8  Ciclo contendo um vértice
9  Verificar subgrafo
10 União com outro grafo
11 Intersecção com outro grafo
12 Diferença simétrica com outro grafo
13 Gerar grafo sem um vértice
14 Gerar grafo sem uma aresta
15 Fundir dois vértices
16 Verificar se é Euleriano
17 Procurar ciclo Hamiltoniano
18 Verificar se é uma ÁRVORE
19 Encontrar CENTRO(S) da árvore
20 Calcular excentricidade dos vértices da árvore
21 Determinar raio da árvore
22 Verificar se A1 é uma árvore subgrafo de G
23 Verificar se A1 é uma árvore de abrangência de G
0  Voltar
"""
        )
        op = input("Escolha: ").strip()

        if op == "0":
            break
        elif op == "1":
            print("|V| =", g.num_vertices())
        elif op == "2":
            print("|E| =", g.num_edges())
        elif op == "3":
            v = prompt_vertex()
            print("Adjacentes:", g.neighbors(v))
        elif op == "4":
            u = prompt_vertex("u")
            v = prompt_vertex("v")
            print("Existe aresta?", g.are_adjacent(u, v))
        elif op == "5":
            v = prompt_vertex()
            print(f"Grau({v}) =", g.degree(v))
        elif op == "6":
            for v, d in g.degrees().items():
                print(f"{v}: grau {d}")
        elif op == "7":
            u = prompt_vertex("origem")
            v = prompt_vertex("destino")
            print("Caminho:", g.simple_path(u, v) or "Nenhum caminho.")
        elif op == "8":
            v = prompt_vertex()
            print("Ciclo:", g.cycle_containing(v) or "Nenhum ciclo.")
        elif op == "9":
            print("Insira o grafo para comparar (subgrafo).")
            other = load_graph_menu()
            if other:
                if other.is_subgraph_of(g):
                    print("O grafo inserido é SUBGRAFO de G.")
                elif g.is_subgraph_of(other):
                    print("G é SUBGRAFO do grafo inserido.")
                else:
                    print("Nenhum é subgrafo do outro.")
        elif op == "10":
            print("Insira o segundo grafo para UNIÃO.")
            other = load_graph_menu()
            if other:
                res = g.union(other)
                print("Grafo resultante (lista de adjacência):")
                for vtx, neigh in res.adjacency_list().items():
                    print(f"{vtx}: {', '.join(neigh)}")
        elif op == "11":
            print("Insira o segundo grafo para INTERSECÇÃO.")
            other = load_graph_menu()
            if other:
                res = g.intersection(other)
                print("Grafo resultante (lista de adjacência):")
                for vtx, neigh in res.adjacency_list().items():
                    print(f"{vtx}: {', '.join(neigh)}")
        elif op == "12":
            print("Insira o segundo grafo para DIFERENÇA SIMÉTRICA.")
            other = load_graph_menu()
            if other:
                res = g.symmetric_difference(other)
                print("Grafo resultante (lista de adjacência):")
                for vtx, neigh in res.adjacency_list().items():
                    print(f"{vtx}: {', '.join(neigh)}")
        elif op == "13":
            v_del = prompt_vertex("vértice a remover")
            try:
                res = g.without_vertex(v_del)
                print("Grafo resultante (lista de adjacência):")
                for vtx, neigh in res.adjacency_list().items():
                    print(f"{vtx}: {', '.join(neigh)}")
            except ValueError as e:
                print(e)
        elif op == "14":
            u = prompt_vertex("u")
            v = prompt_vertex("v")
            try:
                res = g.without_edge(u, v)
                print("Grafo resultante (lista de adjacência):")
                for vtx, neigh in res.adjacency_list().items():
                    print(f"{vtx}: {', '.join(neigh)}")
            except ValueError as e:
                print(e)
        elif op == "15":
            v1 = prompt_vertex("vértice 1")
            v2 = prompt_vertex("vértice 2")
            try:
                res = g.merge_vertices(v1, v2)
                print("Grafo resultante (lista de adjacência):")
                for vtx, neigh in res.adjacency_list().items():
                    print(f"{vtx}: {', '.join(neigh)}")
            except ValueError as e:
                print(e)
        elif op == "16":
            if g.is_eulerian():
                print("O grafo é Euleriano.")
            else:
                print("O grafo não é Euleriano.")
        elif op == "17":
            if g.has_hamiltonian_cycle():
                print("O grafo tem um ciclo Hamiltoniano.")
            else:
                print("O grafo não tem um ciclo Hamiltoniano.")
        elif op == "18":
            if g.is_tree():
                print("Sim, o grafo é uma árvore.")
            else:
                print("Não, o grafo não é uma árvore.")
        elif op == "19":
            try:
                centers = g.find_centers()
                if len(centers) == 1:
                    print(f"O centro da árvore é: {centers[0]}")
                else:
                    print(f"Os centros da árvore são: {', '.join(centers)}")
            except ValueError as e:
                print(f"Erro: {e}")
        elif op == "20":
            try:
                ecc = g.vertex_eccentricities()
                print("Excentricidade dos vértices:")
                for v, e in sorted(ecc.items()):
                    print(f"{v}: {e}")
            except ValueError as e:
                print(f"Erro: {e}")
        elif op == "21":
            try:
                r = g.radius()
                print(f"Raio da árvore: {r}")
            except ValueError as e:
                print(f"Erro: {e}")
        elif op == "22":
            print("Insira a árvore A1 para verificar se é subgrafo de G.")
            a1 = load_graph_menu()
            if a1:
                if g.is_subgraph_tree(a1):
                    print("Sim, A1 é uma árvore que é subgrafo de G.")
                else:
                    print("Não, A1 não é uma árvore que é subgrafo de G.")
        elif op == "23":
            print("Insira a árvore A1 para verificar se é uma árvore de abrangência de G.")
            a1 = load_graph_menu()
            if a1:
                if g.is_spanning_tree(a1):
                    print("Sim, A1 é uma árvore de abrangência de G.")
                else:
                    print("Não, A1 não é uma árvore de abrangência de G.")
        else:
            print("Opção inválida!")
        print()  # separador


# ======================================================================#
#  Loop principal                                                       #
# ======================================================================#


def interactive_menu() -> None:
    graph: Optional[Graph] = None
    print_banner()

    while True:
        print(
            """
====================  MENU PRINCIPAL  ====================
1  Carregar / recriar grafo
2  Exibir representações
3  Operações
4  Ajuda / Tutorial
0  Sair
==========================================================
"""
        )
        cmd = input("Escolha uma opção: ").strip()

        if cmd == "0":
            print("Até logo!")
            break
        elif cmd == "4":
            print_help()
            continue
        elif cmd == "1":
            graph = load_graph_menu()
            if graph:
                print("Grafo carregado com sucesso!")
            continue
        elif graph is None:
            print("Nenhum grafo carregado. Use a opção 1 primeiro.")
            continue

        # --- Exibir representações ------------------------------------
        if cmd == "2":
            print("\n--- Matriz de adjacência ---")
            for r in graph.adjacency_matrix():
                print(" ".join(map(str, r)))
            print("\n--- Matriz de incidência ---")
            for r in graph.incidence_matrix():
                print(" ".join(map(str, r)))
            print("\n--- Lista de adjacência ---")
            for v, neigh in graph.adjacency_list().items():
                print(f"{v}: {', '.join(neigh)}")

        # --- Operações -------------------------------------------------
        elif cmd == "3":
            operations_menu(graph)

        else:
            print("Comando desconhecido!")
        print()


# ======================================================================#
#  Testes rápidos embutidos                                             #
# ======================================================================#


def run_tests() -> None:
    print("Rodando smoke tests...")

    # Grafo quadrado A-B-D-C
    base = Graph()
    for p in ("A B", "B D", "D C", "C A"):
        u, v = p.split()
        base.add_edge(u, v)

    assert base.num_vertices() == 4 and base.num_edges() == 4
    assert base.are_adjacent("A", "B") and not base.are_adjacent("A", "D")

    # Conversões
    assert (
        Graph.from_adjacency_matrix(base.adjacency_matrix(), sorted(base.V)).E
        == base.E
    )
    assert (
        Graph.from_incidence_matrix(base.incidence_matrix(), sorted(base.V)).E
        == base.E
    )

    # CSV round-trip (lista de adjacência)
    import tempfile

    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".csv", mode="w", newline=""
    )
    writer = csv.writer(tmp)
    for v, neigh in base.adjacency_list().items():
        writer.writerow([v] + neigh)
    tmp.close()
    g_csv = Graph.from_adjacency_list(csv_loader.read_adj_list(Path(tmp.name).name))
    os.unlink(tmp.name)
    assert g_csv.E == base.E

    print("🎉  Smoke tests OK!")


# ======================================================================#
#  Entry-point                                                          #
# ======================================================================#


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