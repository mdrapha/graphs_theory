import sys
from pathlib import Path

# Garante que o diretório raiz do projeto esteja no PYTHONPATH
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT)) 