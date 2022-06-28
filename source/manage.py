#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "based.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # from objects import MyServer
    # MyServer.run()

    # from objects import run_app
    # run_app()

    execute_from_command_line(sys.argv)

    # from objects import MyServer, run_app
    #
    # MyServer.run()
    # run_app()


if __name__ == "__main__":
    main()
