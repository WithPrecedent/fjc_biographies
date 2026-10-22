"""Parses the FJC's Biographical Directory of Article III Federal Judges.

Each of the FJC's six files (see `downloader`) becomes a tidy table with
`load`: its columns get short, lower case names (such as "commission_date"
for "Commission Date"), blank cells are missing, the FJC's numbers ("nid",
"sequence", and the years) are whole numbers, and its dates are dates.

`build_roster` combines the files of federal judicial service,
demographics, and professional careers into one table, with a row for each
court that each judge has served on, that codes what researchers usually
want to know about a judge's appointment (such as the party of the
appointing president and the share of senators who voted to confirm the
judge). It is the table that courtpy uses to identify the judges of cases:

```python
import fjc_biographies

tables = fjc_biographies.load_all()
roster = fjc_biographies.build_roster(
    tables['service'], tables['demographics'], tables['career'])
```

The fields that a roster has about judges' careers are made by a rulebook
(see `rules`): the "judges" rulebook in fjc_biographies' "instructions"
folder, unless another is named. It is a CSV file, so fields can be added or
changed in a spreadsheet, without changing fjc_biographies.

Contents:
    build_roster: makes a table with a row for each court that each judge has
        served on.
    code_careers: makes fields from judges' professional careers with a
        rulebook.
    load: returns the tidy table of one of the FJC's files.
    load_all: returns the tidy tables of all of the FJC's files.
    read: returns the tidy table of a CSV file of the directory.
    tidy: returns a table of the directory with names, missing values, and
        types that are easy to use.

"""

from __future__ import annotations

import pathlib
import re
from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd

from . import downloader, options, rules

_APPEALS: str = 'U.S. Court of Appeals'
# The columns of an appointment, which a judge who was reassigned to another
# court keeps from the judge's last appointment.
_APPOINTMENT: tuple[str, ...] = (
    'appointing_president', 'party_of_appointing_president', 'aba_rating',
    'recess_appointment_date', 'senate_vote_type', 'ayes_nays')
_CIRCUIT: re.Pattern[str] = re.compile(r'for the (.+) Circuit\s*$')
# "Middle District of Georgia" and "Districts of North Carolina" both end
# with the state, which any note in parentheses follows.
_DISTRICT: re.Pattern[str] = re.compile(
    r'Districts? of ([A-Za-z ]+?)\s*(?:\(|$)')
_DISTRICT_COURT: str = 'U.S. District Court'
_NUMBERS: frozenset[str] = frozenset({
    'nid', 'jid', 'sequence', 'birth_month', 'birth_day', 'death_month',
    'death_day'})
_PERSONAL: tuple[str, ...] = (
    'nid', 'last_name', 'first_name', 'middle_name', 'suffix', 'birth_year',
    'gender', 'race_or_ethnicity')
_SERVICE: tuple[str, ...] = (
    'nid', 'judge_name', 'court_type', 'court_name', 'commission_date',
    'senior_status_date', 'termination_date', *_APPOINTMENT)
_VOTES: re.Pattern[str] = re.compile(r'(\d+)\s*/\s*(\d+)')
_YEARS: frozenset[str] = frozenset({
    'birth_year', 'death_year', 'degree_year', 'chief_judge_begin',
    'chief_judge_end', 'second_chief_judge_begin', 'second_chief_judge_end'})


def build_roster(
    service: pd.DataFrame | pathlib.Path | str,
    demographics: pd.DataFrame | pathlib.Path | str,
    career: pd.DataFrame | pathlib.Path | str | None = None,
    *,
    rulebook: rules.Rulebook | pathlib.Path | str = 'judges') -> pd.DataFrame:
    """Makes a table with a row for each court that each judge has served on.

    The table has these columns:

    | Column | Meaning |
    | --- | --- |
    | `nid` | The FJC's number for the judge. |
    | `judge` | The judge's name, as the FJC reports it. |
    | `last_name`, `first_name`, `middle_name`, `suffix` | Its parts. |
    | `court`, `court_type` | The court's name and its type. |
    | `circuit_num` | The number of the court's circuit: its own for a court of appeals (12 for the D.C. Circuit and 13 for the Federal Circuit), or for a district court, that of its state now. Missing for other courts. |
    | `start_date`, `end_date`, `senior_date` | The dates the judge's service on the court began (with a commission or a recess appointment) and ended, and the judge took senior status. `end_date` is missing for a judge who is still serving. |
    | `start_year`, `end_year`, `senior_year` | Their years. |
    | `birth_year` | The year the judge was born. |
    | `president` | The president who appointed the judge. |
    | `party` | That president's party: -1 for Democratic and 1 for Republican. Missing for other parties. |
    | `aba_rating` | The American Bar Association's rating, from 1 (not qualified) to 4 (exceptionally well qualified). Missing if there was none, or it was split ("Qualified/Well Qualified"). |
    | `recess` | Whether the judge first took the seat by a recess appointment. |
    | `senate_vote` | The share of senators who voted to confirm the judge (1 for a voice vote). Missing if the vote is not recorded. |
    | `woman`, `minority` | Whether the judge is a woman, and whether the judge's race or ethnicity is anything other than white. Missing if the FJC does not report it. |

    A judge who was reassigned to another court without a new appointment
    (as when the Eleventh Circuit was divided from the Fifth) keeps the
    president, party, rating, recess appointment, and vote of the judge's
    last appointment.

    If `career` is passed, each variable that `rulebook` makes from a
    judge's career (see `code_careers`) is a column too. The "judges"
    rulebook makes "prosecutor", "public_defender", "law_clerk",
    "supreme_court_clerk", "solicitor_general", and "law_professor".

    Args:
        service: the file of federal judicial service, as a path, the table
            that was read from it, or its tidy table.
        demographics: the file of demographics, in any of those forms.
        career: the file of professional careers, in any of those forms.
            Defaults to None, in which case no careers are coded.
        rulebook: the rules that code the careers: a rulebook, or the name of
            a built-in rulebook or the path of a CSV file. Defaults to
            "judges".

    Returns:
        The table, sorted by judge and then by the order of the judge's
            service.

    Raises:
        KeyError: if a file lacks a column that is needed.
        ValueError: if the file of demographics has more than one row for a
            judge, or a variable of `rulebook` has the name of a column of
            the table.

    """
    served = _table(service)
    _require(served, _SERVICE, 'the file of federal judicial service')
    people = _table(demographics)
    _require(people, _PERSONAL, 'the file of demographics')
    order = ['nid', 'sequence'] if 'sequence' in served.columns else ['nid']
    served = served.sort_values(order, kind = 'stable').reset_index(drop = True)
    # A reassigned judge has "None (reassignment)" in place of a president,
    # so the columns of the appointment are taken from the judge's last row
    # that is not a reassignment.
    reassigned = (
        served['appointing_president'].fillna('').str.startswith('None')
        .to_numpy())
    own = pd.Series(np.arange(len(served)), dtype = 'float64').mask(reassigned)
    source = (
        own.groupby(served['nid'], dropna = False).ffill()
        .fillna(-1).astype(int))
    columns = list(_APPOINTMENT)
    appointed = served[columns].reindex(source.to_numpy())
    appointed.index = served.index
    served[columns] = appointed
    # Each row of a judge's service gets the judge's demographics. A judge
    # who is not in the file of demographics has missing ones.
    personal = served[['nid']].merge(
        people[list(_PERSONAL)], on = 'nid', how = 'left',
        validate = 'many_to_one')
    started = served['commission_date'].fillna(
        served['recess_appointment_date'])
    gender = personal['gender'].map({'Female': True, 'Male': False})
    race = personal['race_or_ethnicity']
    roster = pd.DataFrame({
        'nid': served['nid'],
        'judge': served['judge_name'],
        'last_name': personal['last_name'],
        'first_name': personal['first_name'],
        'middle_name': personal['middle_name'],
        'suffix': personal['suffix'],
        'court': served['court_name'],
        'court_type': served['court_type'],
        'circuit_num': pd.array(
            [_circuit(kind, court) for kind, court in zip(
                served['court_type'], served['court_name'], strict = True)],
            dtype = 'Int64'),
        'start_date': started,
        'end_date': served['termination_date'],
        'senior_date': served['senior_status_date'],
        'start_year': _year(started),
        'end_year': _year(served['termination_date']),
        'senior_year': _year(served['senior_status_date']),
        'birth_year': personal['birth_year'].astype('Int64'),
        'president': served['appointing_president'],
        'party': served['party_of_appointing_president'].map(
            options._PARTIES).astype('Int64'),
        'aba_rating': served['aba_rating'].map(
            options._ABA_RATINGS).astype('Int64'),
        'recess': served['recess_appointment_date'].notna(),
        'senate_vote': pd.array(
            [_vote_share(kind, votes) for kind, votes in zip(
                served['senate_vote_type'], served['ayes_nays'],
                strict = True)],
            dtype = 'Float64'),
        'woman': gender.astype('boolean'),
        'minority': (race != 'White').astype('boolean').mask(race.isna())})
    if career is not None:
        coded = code_careers(career, roster['nid'], rulebook = rulebook)
        clashes = [c for c in coded.columns if c in roster.columns]
        if clashes:
            message = (
                f'the rulebook makes {clashes}, which are columns of the '
                f'roster already: rename them in the rulebook')
            raise ValueError(message)
        roster = roster.merge(
            coded, left_on = 'nid', right_index = True, how = 'left')
    return roster


def code_careers(
    career: pd.DataFrame | pathlib.Path | str,
    nids: Iterable[int] | None = None,
    *,
    rulebook: rules.Rulebook | pathlib.Path | str = 'judges') -> pd.DataFrame:
    """Makes fields from judges' professional careers with a rulebook.

    Each judge's positions are put in order, one on each line, as the section
    of text "career", which the rules of `rulebook` search (see `rules`).
    Each variable that the rules make is a field. The "judges" rulebook (in
    fjc_biographies' "instructions" folder) makes a flag for each of six
    kinds of positions: "prosecutor", "public_defender", "law_clerk",
    "supreme_court_clerk", "solicitor_general", and "law_professor".

    Args:
        career: the file of professional careers, as a path, the table that
            was read from it, or its tidy table.
        nids: the numbers of the judges to code. A judge with no career in
            the file gets what the rules make of no text (a flag is False, a
            count is 0, and a label is missing). Defaults to None, in which
            case the judges in `career` are coded.
        rulebook: the rules: a rulebook, or the name of a built-in rulebook
            or the path of a CSV file or a folder of them. Defaults to
            "judges".

    Returns:
        A table with a column for each variable of the rulebook, in order,
            labeled by the judges' numbers ("nid").

    Raises:
        KeyError: if `career` lacks a column that is needed.

    """
    positions = _table(career)
    _require(positions, ['nid', 'position'], 'the file of professional careers')
    book = rules.Rulebook.create(rulebook)
    order = ['nid', 'sequence'] if 'sequence' in positions.columns else ['nid']
    histories = (
        positions.dropna(subset = ['nid', 'position'])
        .sort_values(order, kind = 'stable')
        .groupby('nid')['position'].agg('\n'.join))
    judges = (
        list(histories.index) if nids is None
        else list(dict.fromkeys(int(nid) for nid in nids)))
    coded = [
        book.apply({'career': histories.get(nid, '')}) for nid in judges]
    return pd.DataFrame(
        coded, index = pd.Index(judges, name = 'nid', dtype = 'Int64'),
        columns = book.variables)


def load(
    category: str,
    folder: pathlib.Path | str | None = None,
    *,
    update: bool = False) -> pd.DataFrame:
    """Returns the tidy table of one of the FJC's files.

    The file is downloaded first if it is not in the "raw" folder of
    `folder` (see `downloader.download`).

    Args:
        category: the file's category ("demographics", "service",
            "other_service", "education", "career", or "other_nominations").
        folder: the data folder. Defaults to None, in which case
            `downloader.data_folder()` is used.
        update: whether to download the file again even if it is there, to
            get the judges and corrections since it was downloaded. Defaults
            to False.

    Returns:
        The table (see `tidy`).

    """
    paths = downloader.download(category, folder, overwrite = update)
    return read(paths[category])


def load_all(
    folder: pathlib.Path | str | None = None,
    *,
    update: bool = False) -> dict[str, pd.DataFrame]:
    """Returns the tidy tables of all of the FJC's files.

    Args:
        folder: the data folder. Defaults to None, in which case
            `downloader.data_folder()` is used.
        update: whether to download the files again even if they are there.
            Defaults to False.

    Returns:
        The table of each file (see `tidy`), by its category.

    """
    paths = downloader.download(folder = folder, overwrite = update)
    return {category: read(path) for category, path in paths.items()}


def read(path: pathlib.Path | str, **kwargs: Any) -> pd.DataFrame:
    """Returns the tidy table of a CSV file of the directory.

    The FJC's files are in UTF-8, but a file that was saved again by a
    spreadsheet may be in Windows-1252, which is read too.

    Args:
        path: the path of the file, which may begin with "~" for the user's
            home folder.
        **kwargs: arguments for `pandas.read_csv`.

    Returns:
        The table (see `tidy`).

    """
    path = pathlib.Path(path).expanduser()
    settings: dict[str, Any] = {
        'dtype': str, 'keep_default_na': False, **kwargs}
    try:
        table = pd.read_csv(path, encoding = 'utf-8-sig', **settings)
    except UnicodeDecodeError:
        table = pd.read_csv(path, encoding = 'cp1252', **settings)
    return tidy(table)


def tidy(table: pd.DataFrame) -> pd.DataFrame:
    """Returns a table of the directory that is easy to use.

    A tidy table is not changed, so a table can be tidied more than once.

    Args:
        table: a table of one of the FJC's files, as it was read.

    Returns:
        A new table whose columns have lower case names, with underscores in
            place of spaces and punctuation (and some shorter names, such as
            "position" for "Professional Career", which are in
            `options._COLUMN_NAMES`). Text has no spaces at its ends, and a
            blank cell is missing. "nid", "jid", "sequence", and the months
            and days of births and deaths are whole numbers, as are the
            years, and the columns whose names end in "_date" are dates.
            The empty, unnamed columns at the end of the file of other
            federal judicial service are left out.

    """
    tidied: dict[str, pd.Series] = {}
    for column in table.columns:
        name = _column_name(column)
        values = table[column]
        if name in _NUMBERS:
            values = _number(values, r'(\d+)')
        elif name in _YEARS:
            values = _number(values, r'(\d{4})')
        elif pd.api.types.is_datetime64_any_dtype(values.dtype):
            pass
        elif name.endswith('_date'):
            values = pd.to_datetime(
                _text(values), format = 'mixed', errors = 'coerce')
        elif not pd.api.types.is_numeric_dtype(values.dtype):
            values = _text(values)
        unnamed = not name or name.startswith('unnamed_')
        if unnamed and values.isna().all():
            continue
        tidied[name] = values
    return pd.DataFrame(tidied, index = table.index)


""" Private Functions """


def _circuit(kind: Any, court: Any) -> int | None:
    """Returns the number of the circuit of a court.

    Args:
        kind: the type of the court, such as "U.S. District Court".
        court: the name of the court, such as "U.S. District Court for the
            Middle District of Georgia".

    Returns:
        The number of the circuit of a court of appeals, or that of the state
            or territory of a district court now (12 for the District of
            Columbia), or None for any other court or a name that
            `options._APPEALS_CIRCUITS` or `options._DISTRICT_CIRCUITS` does
            not know.

    """
    if not isinstance(court, str):
        return None
    if kind == _APPEALS:
        match = _CIRCUIT.search(court)
        return options._APPEALS_CIRCUITS.get(match.group(1)) if match else None
    if kind == _DISTRICT_COURT:
        match = _DISTRICT.search(court)
        return options._DISTRICT_CIRCUITS.get(match.group(1)) if match else None
    return None


def _column_name(column: Any) -> str:
    """Returns the tidy name of a column.

    Args:
        column: the name of a column of one of the FJC's files.

    Returns:
        Its name in `options._COLUMN_NAMES`, or else the name in lower case,
            with an underscore in place of each run of spaces and
            punctuation.

    """
    name = str(column).strip().lower()
    if name in options._COLUMN_NAMES:
        return options._COLUMN_NAMES[name]
    return re.sub(r'[^a-z0-9]+', '_', name).strip('_')


def _number(values: pd.Series, pattern: str) -> pd.Series:
    """Returns the whole numbers in a column.

    Args:
        values: numbers, or text with numbers.
        pattern: a pattern whose first group is the number in text.

    Returns:
        The first number in each cell, which is missing if there is none.

    """
    if pd.api.types.is_numeric_dtype(values.dtype):
        return values.astype('Int64')
    found = _text(values).str.extract(pattern, expand = False)
    return pd.to_numeric(found, errors = 'coerce').astype('Int64')


def _require(data: pd.DataFrame, columns: Iterable[str], name: str) -> None:
    """Raises an error if a table lacks columns.

    Args:
        data: the table.
        columns: names of the columns that are needed.
        name: what the table is, for the message.

    Raises:
        KeyError: if a column is missing.

    """
    missing = [c for c in columns if c not in data.columns]
    if missing:
        message = f'{name} needs the columns {missing}, which it does not have'
        raise KeyError(message)


def _table(source: pd.DataFrame | pathlib.Path | str) -> pd.DataFrame:
    """Returns the tidy table of a file.

    Args:
        source: the path of the file, the table that was read from it, or its
            tidy table.

    Returns:
        The tidy table, which is a new table.

    """
    if isinstance(source, pd.DataFrame):
        return tidy(source)
    return read(source)


def _text(values: pd.Series) -> pd.Series:
    """Returns a column as text without spaces at its ends.

    Args:
        values: the column.

    Returns:
        The text of each cell, which is missing if the cell is missing or
            blank.

    """
    cleaned = [
        None if pd.isna(value) or not str(value).strip() else str(value).strip()
        for value in values]
    return pd.Series(cleaned, index = values.index, dtype = 'str')


def _vote_share(kind: Any, votes: Any) -> float | None:
    """Returns the share of senators who voted to confirm a judge.

    Args:
        kind: the type of vote: "Voice", "Roll Call", or anything else.
        votes: the ayes and nays of a roll call, such as "96/2".

    Returns:
        1 for a voice vote, the share of ayes for a roll call, or None if
            there was neither (or no votes are recorded).

    """
    if kind == 'Voice':
        return 1.0
    match = _VOTES.search(votes) if isinstance(votes, str) else None
    if match is None:
        return None
    ayes, nays = int(match.group(1)), int(match.group(2))
    return ayes / (ayes + nays) if ayes + nays else None


def _year(dates: pd.Series) -> pd.Series:
    """Returns the years of a column of dates.

    Args:
        dates: dates, which may be missing.

    Returns:
        The year of each date as a whole number, which is missing if the
            date is.

    """
    years: pd.Series = dates.dt.year.astype('Int64')
    return years
