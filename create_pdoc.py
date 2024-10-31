import os
import pdoc

OUTPUT_DIR = "./docs"

# Programmatically provide settings module
SETTINGS_MODULE = "smarttodo.settings"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_MODULE)

# Setup Django
import django

django.setup()

pdoc.cli(["--output-dir", OUTPUT_DIR, "--force", "--html", "todo"])
