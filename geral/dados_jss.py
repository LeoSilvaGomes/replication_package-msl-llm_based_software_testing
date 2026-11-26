"""Dados das figuras do JSS, calculados a partir dos CSVs de ../ (nenhum número digitado à mão).

    ../data/tabela_de_codigos.csv            ano, fornecedores (Model), técnicas (Prompt Eng., Fine Tuning),
                                        estágios (Stages/Activities) e arquitetura de cada estudo
    ../data/tabela_de_codigos_artefatos.csv  propósito do código e loop (Code purpose, Code loop)

Tudo em contagens de estudos por ano (2023..2026); as figuras convertem para % dos estudos do ano.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))   # graficos/scripts
import dados                    # noqa: E402
import dados_artefatos as da    # noqa: E402

ANOS = [2023, 2024, 2025, 2026]
_E = dados.load()
ESTUDOS_POR_ANO = np.array([int((_E["year"] == a).sum()) for a in ANOS])


def por_ano(mascara):
    """Contagem por ano dos estudos em que a máscara é verdadeira."""
    return [int((mascara & (_E["year"] == a)).sum()) for a in ANOS]


tem = lambda coluna, codigo: _E[coluna].map(lambda c: codigo in c)

# estudos que usam cada fornecedor, por ano (os seis mais usados, em ordem decrescente do total)
_FORNECEDORES = {"OpenAI": "M1", "Meta": "M2", "DeepSeek": "M9", "Google": "M3", "Alibaba (Qwen)": "M10", "Anthropic": "M6"}
fornecedores = {nome: por_ano(tem("vendor", cod)) for nome, cod in _FORNECEDORES.items()}
fornecedores = dict(sorted(fornecedores.items(), key=lambda kv: -sum(kv[1])))

# estudos de cada ano que usam a técnica
tendencias = {
    "Two or more stages": por_ano(_E["stage"].map(len) >= 2),
    "Iterative prompting": por_ano(tem("prompt_engineering", "PE5")),
    "Zero-shot prompting": por_ano(tem("prompt_engineering", "PE2")),
    "Multi-agent": por_ano(tem("architecture", "AR2")),
    "Fine-tuning": por_ano(_E["fine_tuning"].map(len) > 0),
}
# a coluna Architecture está vazia para parte dos estudos; eles não contam como multiagente
SEM_ARQUITETURA = int((_E["architecture"].map(len) == 0).sum())

# propósito do código x loop (N = estudos com A3)
_LOOP = {"Loop closed by the LLM": "CL1", "Direct (no review/repair)": "CL2", "Other automated mechanism": "CL3",
         "Loop closed by a human": "CL4", "LLM + human loops": "CL5", "Human only": "CL6"}
_PROPOSITO = {"Unit testing": "CP1", "Other (fuzz drivers, compilers, ...)": "CP9", "E2E testing": "CP2",
              "Bug reproduction": "CP3", "Security / vulnerability": "CP4", "Acceptance testing": "CP5",
              "Mutation": "CP6", "API testing": "CP7", "Training data": "CP8"}
_t = da.cruzamento("Code purpose", "Code loop")
caminhos = list(_LOOP)
propositos = {nome: [int(_t.loc[cod, c]) for c in _LOOP.values()] for nome, cod in _PROPOSITO.items()}
propositos = dict(sorted(propositos.items(), key=lambda kv: -sum(kv[1])))      # barras em ordem decrescente

if __name__ == "__main__":
    print("estudos por ano:", dict(zip(ANOS, ESTUDOS_POR_ANO)))
    for nome, v in {**fornecedores, **tendencias}.items():
        print(f"{nome:22} {v}  total {sum(v)}")
    print("estudos sem arquitetura informada:", SEM_ARQUITETURA)
    print({k: sum(v) for k, v in propositos.items()})
