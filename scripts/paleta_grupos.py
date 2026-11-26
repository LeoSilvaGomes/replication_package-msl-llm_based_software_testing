"""Paletas dos gráficos por artefato: uma família de cor para cada grupo.

    input        verde
    code         vermelho
    instruction  azul
    oracle       laranja

Cada família parte das cores que os gráficos originais já usavam (ANCORAS). A rampa passa por
essas cores, no espaço CIELAB, e os tons pedidos são escolhidos com saltos iguais de claridade (L*),
para que tons vizinhos fiquem sempre bem separados sem perder a saturação da família.

Uso (com graficos/scripts no sys.path):
    from paleta_grupos import tons_grupo, CINZA_OUTROS
    claro, medio, escuro = tons_grupo("input", 3)
"""
import numpy as np

from paleta import _hex_para_lab, _lab_para_hex

# cores dos gráficos originais de cada grupo, da mais clara à mais escura
ANCORAS = {
    "input": ["#e9f1ea", "#cfe0d1", "#9fbeaa", "#5f8c73", "#1f3f30"],
    "code": ["#fbd4c5", "#f99779", "#f3694a", "#ec3c22", "#c22d19", "#981e11", "#430000"],
    "instruction": ["#f3f8ff", "#d9e8ff", "#a9caff", "#5f95e6", "#254a8a"],
    "oracle": ["#fff6e6", "#ffe3b3", "#ffc86a", "#e49a2a", "#8a4f0a"],
}

CINZA_OUTROS = "#c8c8c8"      # categorias "Other"
CINZA_INDEFINIDO = "#e6e6e6"  # "Undefined" / "Unspecified"


def tons_grupo(grupo, n, inicio=0.0, fim=1.0):
    """n tons do grupo, do mais claro (inicio) ao mais escuro (fim), com saltos iguais de claridade."""
    lab = np.array([_hex_para_lab(c) for c in ANCORAS[grupo]])
    L = lab[:, 0]                                    # decrescente: da âncora clara à escura
    alvos = L[0] + (L[-1] - L[0]) * np.linspace(inicio, fim, n)
    cores = []
    for alvo in alvos:
        i = int(np.clip(np.searchsorted(-L, -alvo, side="right") - 1, 0, len(L) - 2))
        f = (alvo - L[i]) / (L[i + 1] - L[i])
        cores.append(_lab_para_hex(lab[i] + (lab[i + 1] - lab[i]) * f))
    return cores


def cor_texto_legivel(hex_cor):
    """Preto ou branco, o que tiver mais contraste sobre a cor."""
    r, g, b = (int(hex_cor[i:i + 2], 16) for i in (1, 3, 5))
    return "black" if 0.299 * r + 0.587 * g + 0.114 * b > 150 else "white"
