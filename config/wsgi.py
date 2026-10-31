"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()


def _bootstrap():
    from django.core.management import call_command
    from programs.models import Program

    call_command("migrate", interactive=False)
    try:
        call_command("collectstatic", interactive=False, verbosity=0)
    except Exception as exc:
        print(f"collectstatic skipped: {exc}", flush=True)
    if not Program.objects.exists():
        call_command("seed_demo")


if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV") or os.environ.get("VERCEL_URL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    try:
        _bootstrap()
    except Exception as exc:
        print(f"VBADRAN bootstrap failed: {exc}", flush=True)
