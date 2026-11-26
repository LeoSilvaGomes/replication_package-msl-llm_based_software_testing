"""Dados dos gráficos de atividades e estágios, calculados a partir dos CSVs.

Fontes:
    ../data/tabela_de_codigos.csv   atividades e estágios de cada estudo (coluna Stages/Activities)
    taxonomia_atividades.csv        nomes dos estágios e das atividades usados nos gráficos

Nada aqui é digitado à mão: as contagens saem da tabela. Os nomes das variáveis são os mesmos
que os notebooks antigos importavam de `activities_data.py` e `dados_501.py`.

Estágio de um estudo: o rótulo T escrito na tabela (ex.: `T2(A3, A5)` é estágio 2), como no artigo.
"""
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "scripts"))
import dados  # noqa: E402  (graficos/scripts/dados.py)

# ----------------------------------------------------------------------------- taxonomia
TAXONOMIA = pd.read_csv(AQUI / "taxonomia_atividades.csv", dtype=str)
_num = lambda codigo: int(codigo[1:])                                   # 'A10' -> 10, 'T2' -> 2

ACTIVITY_ORDER = [_num(a) for a in TAXONOMIA["atividade"]]
STAGE_ORDER = sorted({_num(t) for t in TAXONOMIA["estagio"]})
ACTIVITY_NAMES = {_num(a): r.replace("\\n", "\n") for a, r in zip(TAXONOMIA["atividade"], TAXONOMIA["rotulo_grafico"])}
STAGE_NAMES = {_num(t): n for t, n in zip(TAXONOMIA["estagio"], TAXONOMIA["nome_estagio"])}
ACTIVITY_STAGE = {_num(a): _num(t) for a, t in zip(TAXONOMIA["atividade"], TAXONOMIA["estagio"])}

# para o diagrama de estágios: [(T1, nome, [(A1, texto), ...]), ...]
ESTAGIOS_DIAGRAMA = [
    (t, g["nome_estagio"].iloc[0], list(zip(g["atividade"], g["rotulo_diagrama"])))
    for t, g in TAXONOMIA.groupby("estagio", sort=False)
]

# ----------------------------------------------------------------------------- estudos
_ESTUDOS = dados.load()


def load_study_activities():
    """{S ID: conjunto de atividades (números)} para os 501 estudos."""
    return {sid: {_num(a) for a in acts} for sid, acts in zip(_ESTUDOS["sid"], _ESTUDOS["activity"])}


def load_study_stages(study_activities=None):
    """{S ID: conjunto de estágios (números)}, pelo rótulo T escrito na tabela."""
    return {sid: {_num(t) for t in ts} for sid, ts in zip(_ESTUDOS["sid"], _ESTUDOS["stage"])}


_ATIVIDADES = load_study_activities()
_ESTAGIOS = load_study_stages()

# ----------------------------------------------------------------------------- contagens
# estudos por atividade (barras A1–A13)
CONTAGEM_ATIVIDADES = {a: sum(a in acts for acts in _ATIVIDADES.values()) for a in ACTIVITY_ORDER}

# estudos cujo conjunto de estágios é exatamente a chave (diagrama de Venn)
_regioes = Counter(frozenset(s) for s in _ESTAGIOS.values() if s)
REGIOES_VENN = {frozenset(c): _regioes.get(frozenset(c), 0)
                for c in [{1}, {2}, {3}, {4}, {1, 2}, {1, 3}, {1, 4}, {2, 3}, {2, 4}, {3, 4},
                          {1, 2, 3}, {1, 2, 4}, {1, 3, 4}, {2, 3, 4}, {1, 2, 3, 4}]}

# estudos que passam por cada estágio (pizza)
TOTAL_ESTAGIO = {s: sum(n for k, n in REGIOES_VENN.items() if s in k) for s in STAGE_ORDER}

# estudos que passam pelos estágios i e j (heatmap; diagonal = TOTAL_ESTAGIO)
COOCORRENCIA_ESTAGIOS = {(i, j): sum(n for k, n in REGIOES_VENN.items() if i in k and j in k)
                         for i in STAGE_ORDER for j in STAGE_ORDER}

# ----------------------------------------------------------------------------- combinações de atividades
MINIMO = 3                                   # o UpSet truncado mostra combinações com pelo menos 3 estudos
_ARTEFATO = [3, 4, 5, 6]                     # atividades que geram artefato (T2)

_combos = Counter(frozenset(acts) for acts in _ATIVIDADES.values() if acts)
TOTAL_CICLOS = sum(_combos.values())         # estudos com pelo menos uma atividade

# combinação EXATA de atividades -> estudos, só as com >= MINIMO, em ordem decrescente
COMBINACOES = sorted(((set(c), n) for c, n in _combos.items() if n >= MINIMO),
                     key=lambda par: (-par[1], len(par[0]), sorted(par[0])))
CICLOS_MOSTRADOS = sum(n for _, n in COMBINACOES)
CICLOS_NAO_MOSTRADOS = TOTAL_CICLOS - CICLOS_MOSTRADOS
COMBINACOES_NAO_MOSTRADAS = sum(1 for n in _combos.values() if n < MINIMO)

# estudos em que cada atividade aparece, contando só as combinações mostradas
CICLOS_POR_ATIVIDADE = {a: sum(n for c, n in COMBINACOES if a in c) for a in ACTIVITY_ORDER}
CICLOS_POR_ATIVIDADE = {a: n for a, n in CICLOS_POR_ATIVIDADE.items() if n > 0}

_ordena = lambda grupo: sorted(grupo, key=lambda a: -CICLOS_POR_ATIVIDADE[a])
ATIVIDADES_ARTEFATO = _ordena([a for a in CICLOS_POR_ATIVIDADE if a in _ARTEFATO])
ATIVIDADES_APOIO = _ordena([a for a in CICLOS_POR_ATIVIDADE if a not in _ARTEFATO])
ORDEM = ATIVIDADES_ARTEFATO + ATIVIDADES_APOIO


def _coocorrencia():
    """Matriz na ordem de ORDEM: fora da diagonal, estudos com as duas atividades; diagonal, só com a atividade."""
    pos = {a: i for i, a in enumerate(ORDEM)}
    m = np.zeros((len(ORDEM), len(ORDEM)), dtype=int)
    for combo, n in COMBINACOES:
        if len(combo) == 1:
            a = next(iter(combo))
            m[pos[a], pos[a]] += n
        for a in combo:
            for b in combo:
                if a != b:
                    m[pos[a], pos[b]] += n
    return m


COOCORRENCIA = _coocorrencia()

if __name__ == "__main__":
    print("estudos:", len(_ESTUDOS), "| com atividade:", TOTAL_CICLOS)
    print("por atividade:", CONTAGEM_ATIVIDADES)
    print("por estágio:", TOTAL_ESTAGIO)
    print("regiões do Venn:", {"+".join(f"T{s}" for s in sorted(k)): v for k, v in REGIOES_VENN.items()})
    print(f"combinações com >= {MINIMO} estudos: {len(COMBINACOES)} ({CICLOS_MOSTRADOS} estudos); "
          f"não mostradas: {COMBINACOES_NAO_MOSTRADAS} ({CICLOS_NAO_MOSTRADOS} estudos)")
    print("ordem das linhas:", ORDEM)
