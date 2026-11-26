"""Executa todos os notebooks de gráficos e regrava as imagens.

    python scripts/gerar_graficos.py            # todos os grupos
    python scripts/gerar_graficos.py code input # só alguns grupos (nomes das pastas)

Cada notebook roda dentro da própria pasta e salva as imagens (PNG e PDF) ao lado dele.
Antes, regenera data/insumo_graficos.csv a partir de data/tabela_de_codigos.csv.
"""
import sys
import warnings
from pathlib import Path

import nbformat
from nbclient import NotebookClient

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parent.parent          # graficos/
GRUPOS = ["geral", "input", "code", "instruction", "oracle"]


def main(grupos):
    sys.path.insert(0, str(RAIZ / "scripts"))
    import dados
    dados.tidy().to_csv(dados.OUTPUT, index=False, encoding="utf-8")

    erros = 0
    for grupo in grupos:
        for caminho in sorted((RAIZ / grupo).glob("*.ipynb")):
            nb = nbformat.read(caminho, as_version=4)
            for celula in nb.cells:
                if celula.cell_type == "code":
                    celula.outputs, celula.execution_count = [], None
            try:
                NotebookClient(nb, timeout=600, resources={"metadata": {"path": str(caminho.parent)}}).execute()
                nbformat.write(nb, caminho)
                print(f"ok    {grupo}/{caminho.name}")
            except Exception as exc:  # noqa: BLE001
                erros += 1
                print(f"ERRO  {grupo}/{caminho.name}: {str(exc).strip().splitlines()[-1]}")
    print(f"{erros} erro(s)")
    return erros


if __name__ == "__main__":
    pedidos = sys.argv[1:] or GRUPOS
    desconhecidos = [g for g in pedidos if g not in GRUPOS]
    if desconhecidos:
        sys.exit(f"grupo desconhecido: {', '.join(desconhecidos)} (use: {', '.join(GRUPOS)})")
    sys.exit(1 if main(pedidos) else 0)
