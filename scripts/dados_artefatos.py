"""Dados dos gráficos por artefato (instruction, input, oracle, code), lidos dos CSVs de ../data.

    tabela_de_codigos_artefatos.csv   códigos de cada estudo por artefato (formato, consumidor, loop...)
    legenda_dos_codigos_artefatos.csv significado de cada código
    tabela_de_codigos.csv             técnicas de prompt, fine-tuning e atividades de cada estudo

Uso em um notebook de uma subpasta de graficos/:
    import sys; sys.path.insert(0, "../scripts")
    import dados_artefatos as da
    da.contagem("Input context")                      # estudos por código
    da.cruzamento("Input value", "Input consumer")    # tabela código x código
    da.tecnicas("A5")                                 # técnicas de prompt e de fine-tuning dos estudos com A5
"""
from pathlib import Path

import pandas as pd

import dados

DATA = Path(__file__).resolve().parent.parent / "data"      # graficos/data
ARTEFATOS = pd.read_csv(DATA / "tabela_de_codigos_artefatos.csv", dtype=str).set_index("S ID")
LEGENDA = pd.read_csv(DATA / "legenda_dos_codigos_artefatos.csv", dtype=str)


def codigos(coluna):
    """Códigos possíveis de uma coluna, na ordem da legenda."""
    return LEGENDA.loc[LEGENDA["column"] == coluna, "code"].tolist()


def rotulos(coluna=None):
    """Dicionário código -> rótulo da legenda."""
    lg = LEGENDA if coluna is None else LEGENDA[LEGENDA["column"] == coluna]
    return dict(zip(lg["code"], lg["label"]))


def estudos(coluna):
    """Série S ID -> lista de códigos, só para os estudos que têm o artefato da coluna."""
    s = ARTEFATOS[coluna]
    return s[s != "-"].str.split(", ")


def contagem(coluna):
    """Estudos por código (um estudo conta uma vez por código que carrega)."""
    s = estudos(coluna)
    return pd.Series({c: int(s.map(lambda v: c in v).sum()) for c in codigos(coluna)})


def cruzamento(linhas, colunas):
    """Tabela de estudos: códigos de `linhas` nas linhas, códigos de `colunas` nas colunas.

    Se uma das colunas tem vários códigos por estudo, o estudo conta uma vez por código.
    """
    a, b = estudos(linhas).explode(), estudos(colunas).explode()
    pares = pd.DataFrame({"a": a}).join(pd.DataFrame({"b": b}), how="inner")
    t = pd.crosstab(pares["a"], pares["b"])
    return t.reindex(index=codigos(linhas), columns=codigos(colunas), fill_value=0)


def tecnicas(atividade):
    """Técnicas dos estudos que têm a atividade (ex.: "A5").

    Devolve (prompt, fine_tuning, n_estudos, n_com_fine_tuning); prompt e fine_tuning são
    séries código -> estudos, com os códigos PE1..PE11 e FT1..FT5.
    """
    todos = dados.load()
    sel = todos[todos["activity"].map(lambda a: atividade in a)]
    conta = lambda dim, prefixo, n: pd.Series(
        {f"{prefixo}{i}": int(sel[dim].map(lambda c: f"{prefixo}{i}" in c).sum()) for i in range(1, n + 1)})
    return (conta("prompt_engineering", "PE", 11), conta("fine_tuning", "FT", 5), len(sel),
            int((sel["fine_tuning"].map(len) > 0).sum()))
