"""Tests for exporting the FJC's files and the command line."""

from __future__ import annotations

import pathlib
import warnings

import pandas as pd
from conftest import SERVICE, tables

import fjc_biographies
from fjc_biographies import __main__ as cli

# Where the tests save the roster of the invented judges in both formats, to
# be looked at. The folder is not in the repository (see ".gitignore").
OUTPUT = pathlib.Path(__file__).parent / 'output'


def test_save_both_formats(tmp_path: pathlib.Path) -> None:
    files = tables()
    roster = fjc_biographies.build_roster(
        files['service'], files['demographics'], files['career'])
    formats = {
        'roster_by_appointment.csv': roster,
        'roster_by_judge.csv': fjc_biographies.roster_by_judge(roster)}
    saved = {
        name: pd.read_csv(fjc_biographies.export(table, tmp_path / name))
        for name, table in formats.items()}
    assert len(saved['roster_by_appointment.csv']) == len(SERVICE)
    assert saved['roster_by_judge.csv']['nid'].is_unique
    # The career text is kept in both files, with its line breaks.
    for table in saved.values():
        lynch = table.loc[table['nid'] == 101, 'career'].iloc[0]
        assert lynch.splitlines()[1].startswith('Assistant attorney general')
    # A file that is open in a spreadsheet (which locks it on Windows) is
    # not replaced, which is not a failure of the package.
    for name, table in formats.items():
        try:
            fjc_biographies.export(table, OUTPUT / name)
        except PermissionError:
            warnings.warn(
                f'{OUTPUT / name} was not replaced because it is open in '
                f'another program, such as Excel: close it and run the tests '
                f'again to see the latest version',
                stacklevel = 1)


def test_version() -> None:
    assert fjc_biographies.__version__ == '0.1.0'


def test_run(requests: list[str], data_folder: pathlib.Path) -> None:
    paths = fjc_biographies.run()
    assert list(paths) == [
        'demographics', 'service', 'other_service', 'education', 'career',
        'other_nominations', 'roster_by_appointment', 'roster_by_judge']
    assert paths['roster_by_appointment'] == data_folder / 'roster_by_appointment.csv'
    roster = pd.read_csv(paths['roster_by_appointment'])
    assert len(roster) == len(SERVICE)
    by_judge = pd.read_csv(paths['roster_by_judge'])
    assert len(by_judge) == len({row[0] for row in SERVICE})
    assert by_judge.loc[by_judge['nid'] == 107, 'court_2'].iloc[0].endswith('First Circuit')
    # Dates are written without times.
    assert roster.loc[0, 'start_date'] == '1995-03-17'
    service = pd.read_csv(paths['service'])
    assert service.loc[0, 'commission_date'] == '1995-03-17'
    assert len(requests) == 6
    fjc_biographies.run(update = True)
    assert len(requests) == 12


def test_cli(requests: list[str], tmp_path: pathlib.Path) -> None:
    cli.main(['--data-folder', str(tmp_path)])
    assert (tmp_path / 'roster_by_appointment.csv').is_file()
    assert (tmp_path / 'roster_by_judge.csv').is_file()
    assert len(requests) == 6
    cli.main(['--data-folder', str(tmp_path), '--download-only', '--update'])
    assert len(requests) == 12


def test_cli_download_only(requests: list[str], data_folder: pathlib.Path) -> None:
    cli.main(['--download-only'])
    assert len(requests) == 6
    assert not (data_folder / 'roster_by_judge.csv').exists()
    assert (data_folder / 'raw' / 'demographics.csv').is_file()
