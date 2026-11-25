"""Entry point for ``python3 -m dice``; the CLI itself lives in ``dice.cli``."""

import sys

from .cli import main

sys.exit(main())
