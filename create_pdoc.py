import os
import pdoc

OUTPUT_DIR = "./docs/todo"

# Programmatically provide settings module
SETTINGS_MODULE = "smarttodo.settings"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_MODULE)

# Setup Django
import django

django.setup()

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Generate HTML documentation and output to the specified directory
pdoc.pdoc("todo", output_directory=OUTPUT_DIR, format="html")
