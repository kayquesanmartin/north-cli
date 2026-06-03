# -*- coding: utf-8 -*-
"""
run.py — launcher da Central de Produtividade (instalado na tool home).

A tool home e o diretorio deste arquivo. O pacote `painel/` fica ao lado.

Uso:
  python run.py build        # regenera o dashboard
  python run.py morning      # foco do dia + abre painel
  python run.py wrap-up      # gera resumos do dia
  python run.py open         # abre o painel ja gerado
"""

import sys
from pathlib import Path

HOME = Path(__file__).resolve().parent
sys.path.insert(0, str(HOME))

from painel.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:], HOME))
