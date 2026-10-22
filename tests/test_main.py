"""Tests for exporting the FJC's files and the command line."""

from __future__ import annotations

import pathlib

import pandas as pd
from conftest import SERVICE

import fjc_biographies
from fjc_biographies import __main__ as cli


def test_version() -> None:
    assert fjc_biographies.__version__ == '0.0.1'


def test_run(requests: list[str], data_folder: pathlib.Path) -> None:
    paths = fjc_biographies.run()
    assert list(paths) == [
        'demographics', 'service', 'other_service', 'education', 'career',
        'other_nominations', 'roster']
    assert paths['roster'] == data_folder / 'roster.csv'
    roster = pd.read_csv(paths['roster'])
    assert len(roster) == len(SERVICE)
    # Dates are written without times.
    assert roster.loc[0, 'start_date'] == '1995-03-17'
    service = pd.read_csv(paths['service'])
    assert service.loc[0, 'commission_date'] == '1995-03-17'
    assert len(requests) == 6
    fjc_biographies.run(update = True)
    assert len(requests) == 12


def test_cli(requests: list[str], tmp_path: pathlib.Path) -> None:
    cli.main(['--data-folder', str(tmp_path)])
    assert (tmp_path / 'roster.csv').is_file()
    assert len(requests) == 6
    cli.main(['--data-folder', str(tmp_path), '--download-only', '--update'])
    assert len(requests) == 12


def test_cli_download_only(requests: list[str], data_folder: pathlib.Path) -> None:
    cli.main(['--download-only'])
    assert len(requests) == 6
    assert not (data_folder / 'roster.csv').exists()
    assert (data_folder / 'raw' / 'demographics.csv').is_file()
