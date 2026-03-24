"""
Module entry point for the Tick Listo application.
Allows running the application as a module with `python -m ticklisto`.
"""

from .cli.tick_listo_cli import main

if __name__ == "__main__":
    main()