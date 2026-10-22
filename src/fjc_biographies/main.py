"""Downloads, parses, and exports the FJC's judge biographies in one step.

`run` saves the tidy table of each of the FJC's files (see `parser.tidy`)
and the roster in two formats, by appointment (see `parser.build_roster`)
and by judge (see `parser.roster_by_judge`), as CSV files in the data
folder:

    data_folder/
    ├── raw/                        the FJC's files, as they were downloaded
    ├── demographics.csv            the tidy table of each file, by its
    ├── service.csv                     category
    ├── ...
    ├── roster_by_appointment.csv   a row for each court that each judge
    │                                   served on
    ├── roster_by_judge.csv         a row for each judge, with each of the
    │                                   judge's appointments numbered
    └── martin_quinn_terms.csv      with `martin_quinn`, each justice's
                                        Martin-Quinn score in each term

With `jcs` or `martin_quinn`, the roster has Judicial Common Space or
Martin-Quinn scores (see `scores`).

Contents:
    export: saves a table as a CSV file.
    run: downloads, parses, and exports the FJC's files.

"""

from __future__ import annotations

import logging
import pathlib

import pandas as pd

from . import downloader, parser, rules, scores

logger = logging.getLogger(__name__)


def run(
    folder: pathlib.Path | str | None = None,
    *,
    update: bool = False,
    rulebook: rules.Rulebook | pathlib.Path | str = 'judges',
    jcs: bool = False,
    martin_quinn: bool | pathlib.Path | str = False,
    scores_folder: pathlib.Path | str | None = None) -> dict[
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
        jcs: whether to add each appointment's Judicial Common Space score
            (see `scores.add_jcs`). Defaults to False.
        martin_quinn: whether to add the justices' Martin-Quinn scores (see
            `scores.add_martin_quinn`) and export their scores in each term,
            or the path of the file of the scores ("justices.csv"), which is
            also used for the justices' Judicial Common Space scores.
            Defaults to False.
        scores_folder: the folder for the files that the scores come from.
            Defaults to None, in which case the data folder of
            judicial-common-space is used.

    Returns:
        The path of each CSV file that was saved, by its category, the
            paths of the roster as "roster_by_appointment" and
            "roster_by_judge", and with `martin_quinn`, the path of the
            justices' scores in each term as "martin_quinn_terms".

    Examples:
        >>> import fjc_biographies
        >>> fjc_biographies.run(update = True)  # doctest: +SKIP

    """
    root = pathlib.Path(folder).expanduser() if folder else (
        downloader.data_folder())
    tables = parser.load_all(root, update = update)
    roster = parser.build_roster(
        tables['service'], tables['demographics'], tables['career'],
        rulebook = rulebook)
    # A path names the file of Martin-Quinn scores, and True finds it.
    path = None if isinstance(martin_quinn, bool) else martin_quinn
    if jcs:
        roster = scores.add_jcs(
            roster, root, scores_folder = scores_folder, martin_quinn = path,
            update = update)
    terms = None
    if martin_quinn:
        terms = scores.martin_quinn_terms(
            root, scores_folder = scores_folder, martin_quinn = path,
            update = update and not jcs)
        roster = scores.add_martin_quinn(roster, terms = terms)
    tables['roster_by_appointment'] = roster
    tables['roster_by_judge'] = parser.roster_by_judge(roster)
    if terms is not None:
        tables['martin_quinn_terms'] = terms
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
