#!/usr/bin/env python3
"""
csv_loader.py – utilitários para ler grafos de arquivos CSV
==========================================================

• A pasta *files/* (na mesma raiz deste script) é o único local permitido para
  busca de CSVs.

Funções públicas
----------------
list_csv_files(limit=15)            → lista de nomes *.csv* (máx. `limit`)
read_matrix(name)                   → matriz (lista de listas de int 0/1)
read_adj_list(name)                 → dicionário {vértice: [vizinho1, …]}

As matrizes podem ser de adjacência *ou* incidência; a lista de adjacência
assume que a primeira coluna é o vértice e as demais, seus vizinhos.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Dict, List

# --------------------------------------------------------------------- #
#  Configuração da pasta base                                           #
# --------------------------------------------------------------------- #
BASE_DIR: Path = Path(__file__).resolve().parent / "files"
BASE_DIR.mkdir(exist_ok=True)  # garante existência


# --------------------------------------------------------------------- #
#  Funções internas                                                     #
# --------------------------------------------------------------------- #
def _safe_path(name: str) -> Path:
    """
    Constrói caminho seguro dentro de ./files e impede *path traversal*.
    """
    p = (BASE_DIR / name).resolve()
    if not str(p).startswith(str(BASE_DIR)):
        raise ValueError("Acesso a caminhos fora da pasta 'files' não permitido.")
    if not p.is_file():
        raise FileNotFoundError(f"Arquivo '{name}' não encontrado em 'files/'.")
    return p


# --------------------------------------------------------------------- #
#  API pública                                                          #
# --------------------------------------------------------------------- #
def list_csv_files(limit: int = 15) -> List[str]:
    """
    Retorna até *limit* nomes de arquivos .csv presentes em ./files,
    ordenados alfabeticamente.
    """
    return sorted(f.name for f in BASE_DIR.glob("*.csv"))[:limit]


def _detect_delimiter(sample: str) -> str:
    """Tenta descobrir delimitador entre vírgula e ponto-e-vírgula.

    1. Usa csv.Sniffer se possível.
    2. Caso falhe (ValueError), decide com base em qual caractere aparece mais.
    3. Fallback final = vírgula.
    """
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;")
        return dialect.delimiter
    except csv.Error:
        # Heurística simples
        comma = sample.count(",")
        semi = sample.count(";")
        if semi > comma:
            return ";"
        return ","


def read_matrix(name: str) -> List[List[int]]:
    """
    Lê *name* (CSV) como matriz de 0/1. Aceita vírgula ou ponto-e-vírgula.
    Retorna lista de listas de int.

    Raises
    ------
    ValueError – se contiver valores diferentes de 0/1 ou linhas de tamanhos
                 diferentes.
    """
    path = _safe_path(name)
    with path.open(newline="") as fh:
        sample = fh.read(1024)
        fh.seek(0)
        delim = _detect_delimiter(sample)
        reader = csv.reader(fh, delimiter=delim)
        matrix: List[List[int]] = []
        for row in reader:
            if not row:  # ignora linhas vazias
                continue
            values = [cell.strip() for cell in row if cell.strip() != ""]
            ints: List[int] = []
            for cell in values:
                if cell not in {"0", "1"}:
                    raise ValueError(
                        f"Valor inválido '{cell}' em {name}; use apenas 0 ou 1."
                    )
                ints.append(int(cell))
            matrix.append(ints)

    # verificação de retangularidade
    if not matrix:
        raise ValueError("Arquivo CSV está vazio.")
    width = len(matrix[0])
    if any(len(r) != width for r in matrix):
        raise ValueError("Matriz não retangular (linhas com tamanhos diferentes).")
    return matrix


def read_adj_list(name: str) -> Dict[str, List[str]]:
    """
    Lê *name* (CSV) como lista de adjacência.
    Espera formato: *vértice, viz1, viz2, ...* (qualquer quantidade de colunas).

    Retorna dict {vertex: [neighbors]}.
    """
    path = _safe_path(name)
    with path.open(newline="") as fh:
        sample = fh.read(1024)
        fh.seek(0)
        delim = _detect_delimiter(sample)
        reader = csv.reader(fh, delimiter=delim)
        adj: Dict[str, List[str]] = {}
        for row in reader:
            if not row:
                continue
            cells = [c.strip() for c in row if c.strip() != ""]
            v, *neigh = cells
            if v in adj:
                raise ValueError(f"Vértice '{v}' aparece mais de uma vez em {name}.")
            # remove vizinhos duplicados mantendo ordem
            unique = []
            seen = set()
            for n in neigh:
                if n not in seen:
                    unique.append(n)
                    seen.add(n)
            adj[v] = unique
    return adj