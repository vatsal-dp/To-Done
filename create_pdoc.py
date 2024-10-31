import os
import pdoc

OUTPUT_DIR = "./docs"

# Programmatically provide settings module
SETTINGS_MODULE = "smarttodo.settings"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_MODULE)

# Setup Django
import django

django.setup()

doc = pdoc.pdoc("todo")
with open(os.path.join(OUTPUT_DIR, "todo.html"), "w") as file:
    file.write(doc)
