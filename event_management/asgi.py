"""
ASGI config for event_management project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')


port = int(os.environ.get("PORT", 8000))  # Default to 8000 if PORT is not set

