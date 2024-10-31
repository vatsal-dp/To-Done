import os
import pdoc
from pathlib import Path

OUTPUT_DIR = Path("./docs/todo")

SETTINGS_MODULE = "smarttodo.settings"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_MODULE)

import django
django.setup()

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

pdoc.pdoc("todo", output_directory=OUTPUT_DIR)
