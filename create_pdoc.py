import os
import pdoc

OUTPUT_DIR = "./docs"

# Programmatically provide settings module
SETTINGS_MODULE = "smarttodo.settings"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_MODULE)

# Setup Django
import django

django.setup()

if __name__ == "__main__":
    # Generate HTML documentation
    pdoc.pdoc(
        "todo",  # module to document
        output_directory=OUTPUT_DIR,
        format="html"
    )
