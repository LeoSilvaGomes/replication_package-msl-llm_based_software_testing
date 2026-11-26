"""Cores do grupo code (família vermelha), iguais em todos os gráficos do grupo.

Loop de revisão/reparo (códigos CL1..CL6) e forma como a entrada chega ao LLM (CR1..CR4).
"Other" fica em cinza: não é um tipo de loop nem de entrada.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))   # graficos/scripts
from paleta_grupos import tons_grupo, CINZA_OUTROS, CINZA_INDEFINIDO  # noqa: E402,F401

# cinco tons do claro ao escuro, com saltos iguais de claridade
_t = tons_grupo("code", 5)
LOOP = {            # código: (rótulo, cor)
    "CL2": ("Direct (no review or repair)", _t[0]),
    "CL4": ("Loop closed by a human", _t[1]),
    "CL1": ("Loop closed by the LLM", _t[2]),
    "CL6": ("Human only", _t[3]),
    "CL5": ("Chained loops (LLM + human)", _t[4]),
    "CL3": ("Other mechanism", CINZA_OUTROS),
}

# três tons bem separados
_r = tons_grupo("code", 3, inicio=0.05, fim=0.92)
ROTA = {
    "CR2": ("Untreated source code", _r[0]),
    "CR1": ("Preprocessed by deterministic tool", _r[1]),
    "CR3": ("Output of a previous LLM call", _r[2]),
    "CR4": ("Other (NL requirements, specs, bug reports)", CINZA_OUTROS),
}

# técnicas: prompt engineering escuro, fine-tuning claro
COR_TECNICA = tons_grupo("code", 5)[3]
COR_FINETUNING = tons_grupo("code", 5)[1]
