import os
import shutil
import pdoc
from pathlib import Path

OUTPUT_DIR = Path("./docs/todo")

if OUTPUT_DIR.exists():
    shutil.rmtree(OUTPUT_DIR)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SETTINGS_MODULE = "smarttodo.settings"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_MODULE)

import django
django.setup()

pdoc.pdoc("todo", output_directory=OUTPUT_DIR)
