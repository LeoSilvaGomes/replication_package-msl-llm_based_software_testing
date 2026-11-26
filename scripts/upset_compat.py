"""UpSet compatível com pandas 3.

O upsetplot 0.9 preenche os estilos dos pontos da matriz com
`styles[col].fillna(..., inplace=True)`. No pandas 3 (copy-on-write) essa chamada
não altera o DataFrame, e os pontos ficam com cor de borda/linha NaN, o que faz o
matplotlib falhar ("Invalid RGBA argument: nan"). Esta subclasse aplica os mesmos
valores padrão da biblioteca logo antes do desenho.

Uso:  from upset_compat import UpSet   (no lugar de `from upsetplot import UpSet`)
"""
import matplotlib.axes as maxes
import pandas as pd
from upsetplot import UpSet as _UpSet


class UpSet(_UpSet):
    def plot_matrix(self, ax):
        original = maxes.Axes.scatter
        cor_padrao = self._facecolor

        def scatter(eixo, *args, **kwargs):
            if "facecolors" in kwargs:
                face = pd.Series(kwargs["facecolors"], dtype="object").fillna(cor_padrao)
                kwargs["facecolors"] = face.tolist()
                if "edgecolors" in kwargs:
                    borda = pd.Series(kwargs["edgecolors"], dtype="object")
                    kwargs["edgecolors"] = borda.where(borda.notna(), face).tolist()
            if "linewidths" in kwargs:
                kwargs["linewidths"] = pd.Series(kwargs["linewidths"], dtype="float").fillna(1).tolist()
            if "linestyles" in kwargs:
                kwargs["linestyles"] = pd.Series(kwargs["linestyles"], dtype="object").fillna("solid").tolist()
            return original(eixo, *args, **kwargs)

        maxes.Axes.scatter = scatter
        try:
            return super().plot_matrix(ax)
        finally:
            maxes.Axes.scatter = original
