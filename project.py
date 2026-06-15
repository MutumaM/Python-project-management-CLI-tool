

import json
import os
import argparse
from datetime import datetime

# Try to import rich for pretty output, fallback to plain print if not installed
try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# DATA FILE PATH


DATA_FILE = "data.json"


# CLASSES

class Person:
    """Base class with a name."""
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name