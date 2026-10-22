"""Downloads and parses the FJC Biographical Directory of Article III Federal Judges"""

from __future__ import annotations

from .downloader import data_folder, download
from .main import export, run
from .parser import build_roster, code_careers, load, load_all, read, tidy
from .rules import Rulebook

__version__ = '0.0.1'

__author__: str = 'Corey Rayburn Yung'

__all__: list[str] = [
    'Rulebook', 'build_roster', 'code_careers', 'data_folder', 'download',
    'export', 'load', 'load_all', 'read', 'run', 'tidy']
