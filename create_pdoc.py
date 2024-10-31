import os
import pdoc

OUTPUT_DIR = "./docs/todo"

SETTINGS_MODULE = "smarttodo.settings"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_MODULE)

import django
django.setup()

os.makedirs(OUTPUT_DIR, exist_ok=True)

pdoc.pdoc("todo", output_directory=OUTPUT_DIR)
