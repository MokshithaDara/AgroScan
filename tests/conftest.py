import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# Ensure tests do not use developer machine paths.
os.environ.setdefault("SQLITE_PATH", str(ROOT / "tests" / ".tmp_agroscan.db"))
