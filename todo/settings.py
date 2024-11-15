"""
This module defines settings for the todo app.
"""
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'clemsonbetter@gmail.com'
EMAIL_HOST_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

INSTALLED_APPS = [
    # other installed apps
    'crispy_forms',  # Ensure crispy_forms is listed here
    'crispy_bootstrap4',  # Add this if you're using the Bootstrap 4 template pack
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'  # or 'bootstrap5' if you're using Bootstrap 5

DEBUG = True
