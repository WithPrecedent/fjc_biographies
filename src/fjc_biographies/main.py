"""Downloads, parses, and exports the FJC's judge biographies in one step.

`run` saves the tidy table of each of the FJC's files (see `parser.tidy`)
and the roster (see `parser.build_roster`) as CSV files in the data folder:

    data_folder/
    ├── raw/                the FJC's files, as they were downloaded
    ├── demographics.csv    the tidy table of each file, by its category
    ├── service.csv
    ├── ...
    └── roster.csv          a row for each court that each judge served on

Contents:
    export: saves a table as a CSV file.
    run: downloads, parses, and exports the FJC's files.

"""

from __future__ import annotations

import logging
import pathlib

import pandas as pd

from . import downloader, parser, rules

logger = logging.getLogger(__name__)


def run(
    folder: pathlib.Path | str | None = None,
    *,
    update: bool = False,
    rulebook: rules.Rulebook | pathlib.Path | str = 'judges') -> dict[
        str, pathlib.Path]:
    """Downloads, parses, and exports the FJC's files.

    Args:
        folder: the data folder. Defaults to None, in which case
            `downloader.data_folder()` is used.
        update: whether to download the files again even if they are there,
            to get the judges and corrections since they were downloaded.
            Defaults to False.
        rulebook: the rules that make the roster's fields about judges'
            careers (see `parser.code_careers`). Defaults to "judges".

    Returns:
        The path of each CSV file that was saved, by its category, and the
            path of the roster as "roster".

    Examples:
        >>> import fjc_biographies
        >>> fjc_biographies.run(update = True)  # doctest: +SKIP

    """
    root = pathlib.Path(folder).expanduser() if folder else (
        downloader.data_folder())
    tables = parser.load_all(root, update = update)
    tables['roster'] = parser.build_roster(
        tables['service'], tables['demographics'], tables['career'],
        rulebook = rulebook)
    return {
        name: export(table, root / f'{name}.csv')
        for name, table in tables.items()}


def export(table: pd.DataFrame, path: pathlib.Path | str) -> pathlib.Path:
    """Saves a table as a CSV file.

    Dates are written as "YYYY-MM-DD", and missing values as blank cells.

    Args:
        table: the table.
        path: where to save it. Its folder is created if needed.

    Returns:
        The path the table was saved to.

    """
    saved = pathlib.Path(path).expanduser()
    saved.parent.mkdir(parents = True, exist_ok = True)
    table.to_csv(
        saved, index = False, encoding = 'utf-8', date_format = '%Y-%m-%d')
    logger.info('Saved %s rows to %s.', len(table), saved.name)
    return saved
