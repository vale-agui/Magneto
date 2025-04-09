#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

def main():
    """Run administrative tasks."""
    BASE_DIR = Path(__file__).resolve().parent
    load_dotenv(BASE_DIR / ".env")

    if __name__ == "__main__":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ingenieriaSoftware.settings")
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ingenieriaSoftware.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()




