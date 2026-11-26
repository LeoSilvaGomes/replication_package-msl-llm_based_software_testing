"""Reads the code table and turns it into the input of the charts.

Files (in ../data):
    tabela_de_codigos.csv     one row per study, codes separated by commas (sheet `code_table` plus the year)
    legenda_dos_codigos.csv   meaning of each code

Use from a notebook or another script:
    import dados
    studies = dados.load()               # one row per study, each code column as a list
    tidy = dados.tidy()                  # one row per study and code (long format)
    dados.count("prompt_engineering")    # studies per code of one dimension

Run it directly to check the table and write `insumo_graficos.csv`:
    python dados.py
"""
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent          # graficos/scripts
DATA = HERE.parent / "data"                      # graficos/data
TABLE = DATA / "tabela_de_codigos.csv"
LEGEND = DATA / "legenda_dos_codigos.csv"
OUTPUT = DATA / "insumo_graficos.csv"

# dimension -> (column of the table, prefix of its codes)
DIMENSIONS = {
    "prompt_engineering": ("Prompt Eng.", "PE"),
    "fine_tuning": ("Fine Tuning", "FT"),
    "stage": ("Stages/Activities", "T"),
    "activity": ("Stages/Activities", "A"),
    "vendor": ("Model", "M"),
    "architecture": ("Architecture", "AR"),
}


def codes(cell, prefix):
    """Codes with this prefix written in a cell, in order and without repeats: 'PE2, PE6' -> ['PE2', 'PE6'].

    The code must be a whole word, so 'M1' is not found inside 'M11' or 'ChatGLM2'.
    An empty cell or '-' gives an empty list.
    """
    if not isinstance(cell, str):
        return []
    found = re.findall(rf"(?<![A-Za-z0-9]){prefix}\d+(?![A-Za-z0-9])", cell)
    return list(dict.fromkeys(found))


def legend():
    """Table of the legend: dimension, code, label, stage (stage only for activities)."""
    return pd.read_csv(LEGEND, dtype=str)


def labels():
    """Dictionary code -> label, e.g. {'PE2': 'Zero-shot', ...}."""
    lg = legend()
    return dict(zip(lg["code"], lg["label"]))


def load():
    """One row per study. Each dimension is a column holding the list of codes of the study."""
    raw = pd.read_csv(TABLE, dtype=str)
    studies = pd.DataFrame({"sid": raw["S ID"], "title": raw["Title"].str.strip(), "year": raw["Year"].astype(int)})
    for dimension, (column, prefix) in DIMENSIONS.items():
        studies[dimension] = raw[column].map(lambda cell: codes(cell, prefix))
    return studies


def tidy():
    """Long format: one row per study and code. Columns: sid, year, dimension, code, label.

    For activities the column `stage_written` holds the stage under which the study lists the activity,
    e.g. 'T2(A3, A5)' gives A3 and A5 with stage_written T2.
    """
    raw = pd.read_csv(TABLE, dtype=str).set_index("S ID")
    studies, lab, rows = load(), labels(), []
    for _, study in studies.iterrows():
        written = {}
        cell = raw.loc[study["sid"], "Stages/Activities"]
        if isinstance(cell, str):
            for stage, inside in re.findall(r"(T\d+)\(([^)]*)\)", cell):
                for activity in codes(inside, "A"):
                    written.setdefault(activity, stage)
        for dimension in DIMENSIONS:
            for code in study[dimension]:
                rows.append({"sid": study["sid"], "year": study["year"], "dimension": dimension, "code": code,
                             "label": lab.get(code, ""), "stage_written": written.get(code, "") if dimension == "activity" else ""})
    return pd.DataFrame(rows)


def count(dimension):
    """Studies per code of one dimension (a study counts once per code it carries), with label and % of all studies."""
    studies = load()
    lg = legend()
    lg = lg[lg["dimension"] == dimension]
    n = [int(studies[dimension].map(lambda c: code in c).sum()) for code in lg["code"]]
    return pd.DataFrame({"code": lg["code"].values, "label": lg["label"].values, "studies": n,
                         "percent": [round(100 * v / len(studies), 1) for v in n]})


def check():
    """Problems in the table that affect the charts: codes missing from the legend and studies without a code."""
    studies, known = load(), set(legend()["code"])
    report = []
    for dimension in DIMENSIONS:
        unknown = sorted({c for cs in studies[dimension] for c in cs} - known)
        without = studies.loc[studies[dimension].map(len) == 0, "sid"].tolist()
        report.append({"dimension": dimension, "studies with a code": len(studies) - len(without),
                       "studies without a code": len(without), "codes not in the legend": ", ".join(unknown)})
    return pd.DataFrame(report)


if __name__ == "__main__":
    studies = load()
    print(f"{len(studies)} studies read from {TABLE.name}; per year: {studies['year'].value_counts().sort_index().to_dict()}\n")
    print(check().to_string(index=False), "\n")
    for dimension in DIMENSIONS:
        print(dimension)
        print(count(dimension).to_string(index=False), "\n")
    table = tidy()
    table.to_csv(OUTPUT, index=False, encoding="utf-8")
    print(f"{len(table)} rows written to {OUTPUT.name}")
