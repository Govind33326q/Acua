"""Quick installation check: imports the backend and confirms model + folders exist."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))

import src.api  # noqa: E402

print("BACKEND_IMPORT_OK")
print("MODEL_PATH", src.api.MODEL_PATH, "EXISTS", src.api.MODEL_PATH.exists())
print("OUTPUT_DIR_EXISTS", src.api.OUTPUT_DIR.exists())
print("UI_BUILT", (root / "frontend" / "dist" / "index.html").exists())
