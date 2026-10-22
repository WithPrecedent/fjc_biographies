"""Writes judges' names in the ways that other sources may write them.

The FJC gives each judge's name in parts: first, middle, and last names and a
suffix (such as "Jr." or "III"). Opinions, other datasets, and news write a
judge's name in other ways, so the roster has a column for each way, which can
be matched against them:

| Column | Example |
| --- | --- |
| `name_first_middle_last` | Robert Lanier Anderson |
| `name_first_middle_last_suffix` | Robert Lanier Anderson, III |
| `name_first_middle_initial_last` | Robert L. Anderson |
| `name_first_middle_initial_last_suffix` | Robert L. Anderson, III |
| `name_first_last` | Robert Anderson |
| `name_first_last_suffix` | Robert Anderson, III |

The FJC puts the letters of a name that a judge does not use in square
brackets, as in "R[obert] Lanier Anderson III", who went by "R. Lanier
Anderson". So each column above has the brackets removed ("Robert"), and a
second column, whose name ends in "_bracket_period", has the brackets and the
letters in them replaced with a period ("R."):

| Column | Example |
| --- | --- |
| `name_first_middle_last_bracket_period` | R. Lanier Anderson |
| `name_first_middle_last_suffix_bracket_period` | R. Lanier Anderson, III |
| ... | ... |

For a name without brackets, the two columns are the same. A part of a name
that is missing is left out, so a judge without a middle name has
"Mary Lynch" for both "name_first_middle_last" and "name_first_last", and a
judge without a suffix has no comma.

Contents:
    add_permutations: adds a column for each way of writing judges' names.
    permutations: returns each way of writing a judge's name.

"""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

# The ways of writing a name without its suffix, in order. Each part is
# written as `_format` finds it.
_FORMS: dict[str, tuple[str, ...]] = {
    'first_middle_last': ('first', 'middle', 'last'),
    'first_middle_initial_last': ('first', 'middle_initial', 'last'),
    'first_last': ('first', 'last')}
# The letters in square brackets, such as "obert" in "R[obert]".
_BRACKETS: re.Pattern[str] = re.compile(r'\[([^\]]*)\]')
_PARTS: tuple[str, ...] = ('first_name', 'middle_name', 'last_name', 'suffix')


def add_permutations(table: pd.DataFrame) -> pd.DataFrame:
    """Adds a column for each way of writing judges' names.

    Args:
        table: a table with the columns "first_name", "middle_name",
            "last_name", and "suffix" (such as a roster or the tidy table of
            the file of demographics).

    Returns:
        A new table with the columns of `permutations` after "suffix".

    Raises:
        KeyError: if `table` lacks one of the parts of a name.

    """
    missing = [part for part in _PARTS if part not in table.columns]
    if missing:
        message = (
            f'names are written from the columns {missing}, which the table '
            f'does not have')
        raise KeyError(message)
    written = pd.DataFrame(
        [permutations(*parts) for parts in zip(
            *(table[part] for part in _PARTS), strict = True)],
        index = table.index, columns = columns(), dtype = 'str')
    place = list(table.columns).index('suffix') + 1
    before, after = table.iloc[:, :place], table.iloc[:, place:]
    return pd.concat([before, written, after], axis = 1)


def columns() -> list[str]:
    """Returns the names of the columns that `permutations` makes.

    Returns:
        The names, in order.

    """
    names = []
    for form in _FORMS:
        for suffix in ('', '_suffix'):
            names.extend([
                f'name_{form}{suffix}', f'name_{form}{suffix}_bracket_period'])
    return names


def permutations(
    first: Any,
    middle: Any,
    last: Any,
    suffix: Any = None) -> dict[str, str | None]:
    """Returns each way of writing a judge's name.

    Args:
        first: the first name, such as "R[obert]".
        middle: the middle name or names, such as "Lanier". It may be missing.
        last: the last name, such as "Anderson".
        suffix: the suffix, such as "III". Defaults to None.

    Returns:
        Each way of writing the name, by the name of its column (see the
            module's documentation). All are None if the name has no first
            or last name.

    """
    first, middle, last, suffix = (
        _text(part) for part in (first, middle, last, suffix))
    if not first and not last:
        return dict.fromkeys(columns())
    found: dict[str, str | None] = {}
    for form, parts in _FORMS.items():
        for with_suffix in (False, True):
            name = f'name_{form}{"_suffix" if with_suffix else ""}'
            for brackets, ending in (('remove', ''), ('period', '_bracket_period')):
                cleaned = {
                    'first': _brackets(first, brackets),
                    'middle': _brackets(middle, brackets),
                    'middle_initial': _initial(_brackets(middle, 'remove')),
                    'last': _brackets(last, brackets)}
                written = ' '.join(
                    cleaned[part] for part in parts if cleaned[part])
                if with_suffix and suffix:
                    written = f'{written}, {suffix}'
                found[f'{name}{ending}'] = written
    return found


""" Private Functions """


def _brackets(part: str, how: str) -> str:
    """Removes the square brackets in a part of a name.

    Args:
        part: the part, such as "R[obert]".
        how: "remove" to keep the letters in the brackets ("Robert"), or
            "period" to put a period in place of them ("R.").

    Returns:
        The part without brackets.

    """
    if how == 'remove':
        return _BRACKETS.sub(r'\1', part)
    return _BRACKETS.sub('.', part)


def _initial(middle: str) -> str:
    """Returns the initial of a middle name.

    Args:
        middle: the middle name or names, such as "Lanier" or "Q.".

    Returns:
        The first letter of the first middle name with a period, such as
            "L.", or an empty `str` if there is no middle name.

    """
    letter = next((c for c in middle if c.isalpha()), '')
    return f'{letter.upper()}.' if letter else ''


def _text(part: Any) -> str:
    """Returns a part of a name as text with single spaces.

    Args:
        part: the part, which may be missing.

    Returns:
        The part, or an empty `str` if it is missing.

    """
    if part is None or (not isinstance(part, str) and pd.isna(part)):
        return ''
    return ' '.join(str(part).split())
