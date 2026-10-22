"""Tests for writing judges' names in other ways."""

from __future__ import annotations

import pandas as pd
import pytest
from conftest import tables

import fjc_biographies
from fjc_biographies import names


def test_permutations() -> None:
    written = fjc_biographies.name_permutations('Milton', 'Dale', 'Smith', 'Jr.')
    assert written == {
        'name_first_middle_last': 'Milton Dale Smith',
        'name_first_middle_last_bracket_period': 'Milton Dale Smith',
        'name_first_middle_last_suffix': 'Milton Dale Smith, Jr.',
        'name_first_middle_last_suffix_bracket_period': 'Milton Dale Smith, Jr.',
        'name_first_middle_initial_last': 'Milton D. Smith',
        'name_first_middle_initial_last_bracket_period': 'Milton D. Smith',
        'name_first_middle_initial_last_suffix': 'Milton D. Smith, Jr.',
        'name_first_middle_initial_last_suffix_bracket_period': 'Milton D. Smith, Jr.',
        'name_first_last': 'Milton Smith',
        'name_first_last_bracket_period': 'Milton Smith',
        'name_first_last_suffix': 'Milton Smith, Jr.',
        'name_first_last_suffix_bracket_period': 'Milton Smith, Jr.'}
    assert list(written) == names.columns()


def test_permutations_with_brackets() -> None:
    written = names.permutations('R[obert]', 'Lanier', 'Anderson', 'III')
    # The brackets are removed, or the brackets and the letters in them are
    # replaced with a period.
    assert written['name_first_middle_last'] == 'Robert Lanier Anderson'
    assert written['name_first_middle_last_bracket_period'] == 'R. Lanier Anderson'
    assert written['name_first_middle_last_suffix'] == 'Robert Lanier Anderson, III'
    assert written['name_first_middle_last_suffix_bracket_period'] == 'R. Lanier Anderson, III'
    assert written['name_first_middle_initial_last_bracket_period'] == 'R. L. Anderson'
    assert written['name_first_last'] == 'Robert Anderson'
    assert written['name_first_last_bracket_period'] == 'R. Anderson'


def test_permutations_with_missing_parts() -> None:
    # Without a middle name or a suffix, there are no extra spaces or commas.
    written = names.permutations('Mary', None, 'Lynch', float('nan'))
    assert set(written.values()) == {'Mary Lynch'}
    # A middle name that is an initial keeps a single period.
    assert names.permutations('John', 'Q.', 'Howard')['name_first_middle_initial_last'] == 'John Q. Howard'
    # Spaces are made single, and the initial is that of the first middle name.
    written = names.permutations(' Kim ', 'van  Pelt', 'Doe')
    assert written['name_first_middle_last'] == 'Kim van Pelt Doe'
    assert written['name_first_middle_initial_last'] == 'Kim V. Doe'
    # A name with no first or last name has no permutations.
    assert set(names.permutations(None, None, None).values()) == {None}


def test_add_permutations() -> None:
    people = fjc_biographies.tidy(tables()['demographics'])
    added = names.add_permutations(people)
    columns = list(added.columns)
    # The columns come right after the suffix.
    start = columns.index('suffix') + 1
    assert columns[start:start + len(names.columns())] == names.columns()
    assert columns[start + len(names.columns())] == 'birth_year'
    fields = added.set_index('nid')
    assert fields.loc[108, 'name_first_middle_last_suffix_bracket_period'] == 'R. Lanier Fields, III'
    assert fields.loc[105, 'name_first_last'] == 'Norman Smith'
    assert fields.loc[105, 'name_first_last_bracket_period'] == 'N. Smith'
    assert fields.loc[112, 'name_first_middle_last'] == 'John Marsh'
    with pytest.raises(KeyError, match = 'suffix'):
        names.add_permutations(people.drop(columns = 'suffix'))


def test_roster_has_permutations() -> None:
    files = tables()
    roster = fjc_biographies.build_roster(files['service'], files['demographics'], files['career'])
    assert set(names.columns()) <= set(roster.columns)
    by_judge = fjc_biographies.roster_by_judge(roster)
    # The names describe the judge, so they are not numbered.
    assert 'name_first_last' in by_judge.columns
    assert 'name_first_last_1' not in by_judge.columns
    # A judge who is not in the file of demographics has none.
    missing = fjc_biographies.build_roster(files['service'], files['demographics'].iloc[1:])
    assert missing.loc[missing['nid'] == 101, names.columns()].isna().all(axis = None)
    assert pd.api.types.is_string_dtype(roster['name_first_last'])
