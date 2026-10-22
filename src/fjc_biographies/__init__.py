"""Downloads and parses the FJC Biographical Directory of Article III Federal Judges"""

from __future__ import annotations

from .downloader import data_folder, download
from .main import export, run
from .names import permutations as name_permutations
from .parser import (
    build_roster,
    code_careers,
    load,
    load_all,
    read,
    roster_by_judge,
    tidy,
)
from .rules import Rulebook
from .scores import add_jcs, add_martin_quinn, martin_quinn_terms

__version__ = '0.1.0'

__author__: str = 'Corey Rayburn Yung'

__all__: list[str] = [
    'Rulebook', 'add_jcs', 'add_martin_quinn', 'build_roster', 'code_careers',
    'data_folder', 'download', 'export', 'load', 'load_all',
    'martin_quinn_terms', 'name_permutations', 'read', 'roster_by_judge',
    'run', 'tidy']
