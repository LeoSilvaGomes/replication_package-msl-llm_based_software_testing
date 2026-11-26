"""Paleta de cores compartilhada pelos gráficos do artigo.

Rampa de verde-azulado interpolada no espaço CIELAB (salto de claridade percebida
igual entre tons vizinhos). A ponta clara é #eef5f6; a ponta escura é o #0b5a63
escurecido em ESCURECER pontos de L* (mesmo matiz), para aumentar a diferença entre
os tons. Com ESCURECER = 0 a rampa vai exatamente de #0b5a63 a #eef5f6.

Uso:
    import sys; sys.path.insert(0, "../scripts")   # a partir de uma subpasta de graficos/
    from paleta import TONS, CORES_ESTAGIO, tons, cmap_sequencial
"""
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

COR_ESCURA, COR_CLARA = "#0b5a63", "#eef5f6"
ESCURECER = 20

_M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
_WN = np.array([0.95047, 1.0, 1.08883])
_D = 6 / 29


def _hex_para_lab(h):
    rgb = np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    t = (_M @ lin) / _WN
    f = np.where(t > _D ** 3, np.cbrt(t), t / (3 * _D ** 2) + 4 / 29)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def _lab_para_hex(lab):
    L, a, b = lab
    fy = (L + 16) / 116
    f = np.array([fy + a / 500, fy, fy - b / 200])
    xyz = np.where(f > _D, f ** 3, 3 * _D ** 2 * (f - 4 / 29)) * _WN
    lin = np.clip(np.linalg.solve(_M, xyz), 0, 1)
    rgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
    return "#" + "".join(f"{int(round(v * 255)):02x}" for v in rgb)


_LAB_CLARA = _hex_para_lab(COR_CLARA)
_LAB_ESCURA = _hex_para_lab(COR_ESCURA)
_LAB_ESCURA[0] -= ESCURECER


def tom(t):
    """Cor da rampa na posição t (0 = #eef5f6, 1 = ponta escura)."""
    return _lab_para_hex(_LAB_CLARA + (_LAB_ESCURA - _LAB_CLARA) * t)


def tons(n, inicio=0.0, fim=1.0):
    """n cores da rampa, da mais escura (fim) para a mais clara (inicio)."""
    return [tom(t) for t in np.linspace(fim, inicio, n)]


def cmap_sequencial(nome="paleta", com_branco=True):
    """Colormap contínuo branco → ponta escura (para heatmaps)."""
    pontos = (["#ffffff"] if com_branco else []) + [tom(t) for t in np.linspace(0, 1, 7)]
    return LinearSegmentedColormap.from_list(nome, pontos)


# 6 tons usados nos gráficos (do mais escuro ao mais claro)
TONS = tons(6)   # #002c35 #195057 #50767c #839fa3 #b8c9cc #eef5f6

# 4 estágios (T1..T4): os 4 tons mais escuros, como a escala de cinza original
CORES_ESTAGIO = {1: TONS[0], 2: TONS[1], 3: TONS[2], 4: TONS[3]}

if __name__ == "__main__":
    print("TONS:", TONS)
    print("CORES_ESTAGIO:", CORES_ESTAGIO)
