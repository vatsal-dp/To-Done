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
    # Create documentation generator
    doc = pdoc.pdoc("todo")
    
    # Write HTML files to the output directory
    doc.output_to_files(directory=OUTPUT_DIR)
