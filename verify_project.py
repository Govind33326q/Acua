import os
import sys
from pathlib import Path

root = Path(r'd:\AquaVisionaries\AquaVisinaries\AquaVisinaries')
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import src.api
print('BACKEND_IMPORT_OK')
print('MODEL_PATH_EXISTS', src.api.MODEL_PATH.exists())
print('OUTPUT_DIR_EXISTS', src.api.OUTPUT_DIR.exists())
