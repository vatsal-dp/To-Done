"""
This module defines settings for the todo app.
"""
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'myapp',
    'crispy_forms',  # Ensure crispy_forms is listed here
    'crispy_bootstrap4',
    'django.contrib.messages', 
]


MIDDLEWARE = [
    'django.contrib.messages.middleware.MessageMiddleware',
]


CRISPY_TEMPLATE_PACK = 'bootstrap4'  # or 'bootstrap5' if you're using Bootstrap 5

DEBUG = True
