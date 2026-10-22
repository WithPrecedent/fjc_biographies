"""Tests for parsing the FJC's files and building a roster."""

from __future__ import annotations

import pathlib

import pandas as pd
import pytest
from conftest import APPEALS, DISTRICT, FIRST, NINTH, SERVICE, tables

import fjc_biographies
from fjc_biographies import parser

FLAGS = [
    'prosecutor', 'public_defender', 'law_clerk', 'supreme_court_clerk',
    'solicitor_general', 'law_professor']


@pytest.fixture
def table() -> pd.DataFrame:
    """Returns the roster of the invented judges, labeled by court."""
    files = tables()
    return fjc_biographies.build_roster(
        files['service'], files['demographics'], files['career']).set_index(
            'court', drop = False)


def test_tidy_names_and_types() -> None:
    service = parser.tidy(tables()['service'])
    assert list(service.columns[:5]) == [
        'nid', 'sequence', 'judge_name', 'court_type', 'court_name']
    assert 'ayes_nays' in service.columns
    assert service['nid'].dtype == 'Int64'
    assert pd.api.types.is_datetime64_any_dtype(service['commission_date'])
    assert service['commission_date'].iloc[0] == pd.Timestamp('1995-03-17')
    # Blank text and text of spaces are missing, and text is trimmed.
    assert pd.isna(service['senior_status_date'].iloc[0])
    assert pd.isna(service['recess_appointment_date'].iloc[0])
    assert service['ayes_nays'].iloc[1] == '99/1'
    people = parser.tidy(tables()['demographics'])
    assert people['birth_year'].dtype == 'Int64'
    assert pd.isna(people.set_index('nid').loc[112, 'middle_name'])
    # Tidying a tidy table changes nothing.
    pd.testing.assert_frame_equal(parser.tidy(service), service)


def test_tidy_other_tables() -> None:
    files = tables()
    other = parser.tidy(files['other_service'])
    # The empty, unnamed columns are left out.
    assert list(other.columns) == [
        'nid', 'sequence', 'judge_name', 'type', 'description']
    education = parser.tidy(files['education'])
    assert list(education['degree_year']) == [1971, pd.NA]
    assert pd.isna(education['degree'].iloc[1])
    assert list(parser.tidy(files['career']).columns) == [
        'nid', 'sequence', 'position']
    assert list(parser.tidy(files['other_nominations']).columns) == [
        'nid', 'sequence', 'judge_name', 'description']


def test_tidy_dates_in_either_format() -> None:
    # The FJC's page says that its CSV files write dates as mm/dd/yyyy,
    # although they write them as yyyy-mm-dd.
    dates = parser.tidy(pd.DataFrame({
        'Commission Date': ['11/20/2014', '2014-11-20', '', 'unknown']}))
    assert list(dates['commission_date'][:2]) == [pd.Timestamp('2014-11-20')] * 2
    assert dates['commission_date'][2:].isna().all()


def test_read(tmp_path: pathlib.Path) -> None:
    files = tables()
    path = tmp_path / 'demographics.csv'
    files['demographics'].to_csv(path, index = False)
    assert parser.read(path).loc[0, 'last_name'] == 'Lynch'
    # A file that is not in UTF-8 is read as Windows-1252.
    files['demographics'].loc[0, 'Last Name'] = 'Peña'
    files['demographics'].to_csv(path, index = False, encoding = 'cp1252')
    assert parser.read(path).loc[0, 'last_name'] == 'Peña'


def test_build_roster(table: pd.DataFrame) -> None:
    assert len(table) == len(SERVICE)
    # Rows are sorted by judge and then by the order of the judge's service.
    assert list(table.loc[table['nid'] == 107, 'court_type']) == [DISTRICT, APPEALS]
    lynch = table.loc[FIRST].iloc[0]
    assert lynch['judge'] == 'Lynch, Mary Ann'
    assert (lynch['last_name'], lynch['first_name'], lynch['middle_name']) == ('Lynch', 'Mary', 'Ann')
    assert lynch['circuit_num'] == 1
    assert lynch['start_date'] == pd.Timestamp('1995-03-17')
    assert (lynch['start_year'], lynch['birth_year']) == (1995, 1946)
    assert pd.isna(lynch['end_year']) and pd.isna(lynch['senior_year'])
    assert (lynch['party'], lynch['aba_rating'], lynch['senate_vote']) == (-1, 3, 1.0)
    assert lynch['woman'] and not lynch['minority'] and not lynch['recess']
    by_nid = table.drop_duplicates('nid', keep = 'last').set_index('nid')
    assert list(by_nid.loc[[102, 103, 106], 'aba_rating']) == [2, 4, 1]
    assert pd.isna(by_nid.loc[105, 'aba_rating'])
    assert by_nid.loc[102, 'senate_vote'] == pytest.approx(0.99)
    assert by_nid.loc[103, 'minority'] and by_nid.loc[105, 'minority']
    assert by_nid.loc[110, 'end_year'] == 2017
    assert by_nid.loc[106, 'senior_year'] == 2015
    # A gender that is not reported is missing.
    assert pd.isna(by_nid.loc[113, 'woman'])


def test_build_roster_circuits(table: pd.DataFrame) -> None:
    circuits = table.drop_duplicates('court')['circuit_num']
    assert circuits[NINTH] == 9
    assert circuits['U.S. Court of Appeals for the Eleventh Circuit'] == 11
    assert circuits['U.S. Court of Appeals for the District of Columbia Circuit'] == 12
    assert circuits['U.S. Court of Appeals for the Federal Circuit'] == 13
    assert pd.isna(circuits['Supreme Court of the United States'])
    # A district court's circuit is its state's.
    assert circuits['U.S. District Court for the District of Massachusetts'] == 1
    assert circuits['U.S. District Court for the Southern District of New York'] == 2
    assert parser._circuit(DISTRICT, 'U.S. District Court for the District of Columbia (Supreme Court)') == 12
    assert parser._circuit(DISTRICT, 'U.S. District Court for the Edenton & Wilmington Districts of North Carolina') == 4
    assert parser._circuit(DISTRICT, 'U.S. District Court for the District of Orleans') is None
    assert parser._circuit('Other', 'U.S. Court of International Trade') is None


def test_build_roster_appointments(table: pd.DataFrame) -> None:
    fifth = table.loc['U.S. Court of Appeals for the Fifth Circuit']
    eleventh = table.loc['U.S. Court of Appeals for the Eleventh Circuit']
    # A reassigned judge keeps the appointment of the judge's earlier service.
    assert (fifth['start_year'], fifth['end_year'], eleventh['start_year']) == (1979, 1981, 1981)
    for column in ('president', 'party', 'aba_rating', 'senate_vote'):
        assert eleventh[column] == fifth[column]
    assert eleventh['president'] == 'Jimmy Carter'
    assert eleventh['senate_vote'] == pytest.approx(60 / 90)
    federal = table.loc['U.S. Court of Appeals for the Federal Circuit']
    assert (federal['president'], federal['party']) == ('Barack Obama', -1)
    # A recess appointment starts a judge's service, and a party other than
    # the two of today, an unrecorded vote, and an unknown gender are missing.
    fourth = table.loc['U.S. Court of Appeals for the Fourth Circuit']
    assert fourth['recess'] and fourth['start_year'] == 2000
    assert pd.isna(fourth['senate_vote'])
    supreme = table.loc['Supreme Court of the United States']
    assert pd.isna(supreme['party']) and pd.isna(supreme['woman']) and pd.isna(supreme['minority'])


def test_build_roster_reassignment_takes_whole_appointment() -> None:
    # A reassigned judge takes every column of the appointment from the row
    # above, even one that is missing there.
    files = tables()
    service = files['service']
    service.loc[service['nid'] == 108, 'ABA Rating'] = ''
    service.loc[service['nid'] == 107, 'Appointing President'] = [
        'None (reassignment)', 'George H.W. Bush']
    table = fjc_biographies.build_roster(service, files['demographics'])
    assert table.loc[table['nid'] == 108, 'aba_rating'].isna().all()
    stone = table.loc[table['nid'] == 107]
    assert list(stone['aba_rating']) == [2, 2]


def test_build_roster_careers(table: pd.DataFrame) -> None:
    careers = table.drop_duplicates('nid').set_index('nid')
    assert list(careers.loc[101, FLAGS]) == [True, False, True, False, False, False]
    assert list(careers.loc[102, FLAGS]) == [True, False, False, False, False, False]
    assert list(careers.loc[103, FLAGS]) == [False, True, False, False, False, False]
    assert list(careers.loc[104, FLAGS]) == [False, False, True, True, False, True]
    # A clerkship and the Supreme Court in different positions are not a
    # clerkship at the Supreme Court, and "District" alone is not a prosecutor.
    assert list(careers.loc[105, FLAGS]) == [False, False, True, False, False, False]
    assert careers.loc[113, 'solicitor_general']
    # A judge with no career in the file has no flags.
    assert not careers.loc[106, FLAGS].any()
    assert careers['prosecutor'].dtype == bool


def test_build_roster_from_paths(tmp_path: pathlib.Path) -> None:
    paths = {}
    for kind in ('service', 'demographics'):
        paths[kind] = tmp_path / f'{kind}.csv'
        tables()[kind].to_csv(paths[kind], index = False)
    table = fjc_biographies.build_roster(**paths)
    assert 'prosecutor' not in table.columns
    assert len(table) == len(SERVICE)


def test_build_roster_merges_by_judge() -> None:
    files = tables()
    # A judge who is not in the file of demographics has missing ones.
    table = fjc_biographies.build_roster(files['service'], files['demographics'].iloc[1:])
    lynch = table.loc[table['nid'] == 101].iloc[0]
    assert pd.isna(lynch['last_name']) and pd.isna(lynch['woman'])
    assert table.loc[table['nid'] == 102, 'last_name'].iloc[0] == 'Howard'
    # A judge can only be one row of the demographics.
    twice = pd.concat([files['demographics'], files['demographics'].iloc[:1]])
    with pytest.raises(ValueError, match = 'many-to-one'):
        fjc_biographies.build_roster(files['service'], twice)


def test_build_roster_missing_columns() -> None:
    files = tables()
    with pytest.raises(KeyError, match = 'federal judicial service'):
        fjc_biographies.build_roster(files['service'].drop(columns = 'Court Name'), files['demographics'])
    with pytest.raises(KeyError, match = 'demographics'):
        fjc_biographies.build_roster(files['service'], files['demographics'].drop(columns = 'Gender'))
    with pytest.raises(KeyError, match = 'careers'):
        fjc_biographies.build_roster(files['service'], files['demographics'], files['career'].drop(columns = 'nid'))


def test_code_careers() -> None:
    career = tables()['career']
    flags = fjc_biographies.code_careers(career)
    assert flags.index.name == 'nid'
    assert list(flags.index) == [101, 102, 103, 104, 105, 113]
    assert list(flags.columns) == FLAGS
    assert (flags.dtypes == bool).all()
    # Judges can be chosen, and a judge with no career has no flags.
    chosen = fjc_biographies.code_careers(career, [104, 999, 104])
    assert list(chosen.index) == [104, 999]
    assert not chosen.loc[999].any()


def test_code_careers_with_own_rulebook(tmp_path: pathlib.Path) -> None:
    rules = tmp_path / 'careers.csv'
    rules.write_text(
        'target,variable,kind,pattern,value,ignorecase,dotall,note\n'
        'career,positions,count,\\d{4}-\\d{4},,FALSE,FALSE,\n'
        'career,first_job,section,^[^\\n]*,,FALSE,FALSE,The first position\n'
        'career,kind,label,clerk,clerk,TRUE,FALSE,\n'
        'career,kind,label,attorney,lawyer,TRUE,FALSE,\n'
        'career,years,matches,\\d{4}-\\d{4},,FALSE,FALSE,\n', encoding = 'utf-8')
    coded = fjc_biographies.code_careers(tables()['career'], [101, 102, 103, 106], rulebook = rules)
    assert list(coded.columns) == ['positions', 'first_job', 'kind', 'years']
    assert list(coded['positions']) == [2, 1, 1, 0]
    # The positions are in the order of their sequence numbers.
    assert coded.loc[101, 'first_job'].startswith('Law clerk')
    assert list(coded['kind'][:2]) == ['clerk', 'lawyer']
    assert coded['kind'][2:].isna().all()
    assert coded.loc[101, 'years'] == ['1971-1973', '1973-1974']
    # A roster gets the rulebook's fields in place of the built-in ones.
    files = tables()
    table = fjc_biographies.build_roster(
        files['service'], files['demographics'], files['career'], rulebook = rules)
    assert 'prosecutor' not in table.columns
    assert list(table.loc[table['nid'].isin([101, 106]), 'positions']) == [2, 0]


def test_code_careers_sorts_positions() -> None:
    career = tables()['career'].iloc[::-1]
    book = fjc_biographies.Rulebook.create('judges')
    coded = fjc_biographies.code_careers(career, rulebook = book)
    assert list(coded.index) == [101, 102, 103, 104, 105, 113]


def test_build_roster_rulebook_clash(tmp_path: pathlib.Path) -> None:
    rules = tmp_path / 'clash.csv'
    rules.write_text(
        'target,variable,kind,pattern,ignorecase,dotall\n'
        'career,party,flag,x,TRUE,FALSE\n', encoding = 'utf-8')
    files = tables()
    with pytest.raises(ValueError, match = 'party'):
        fjc_biographies.build_roster(
            files['service'], files['demographics'], files['career'], rulebook = rules)


def test_load(requests: list[str], tmp_path: pathlib.Path) -> None:
    service = fjc_biographies.load('service', tmp_path)
    assert len(requests) == 1
    assert service['court_name'].iloc[0] == FIRST
    assert (tmp_path / 'raw' / 'federal-judicial-service.csv').is_file()
    # A file that was downloaded is read again without downloading it.
    fjc_biographies.load('service', tmp_path)
    assert len(requests) == 1
    fjc_biographies.load('service', tmp_path, update = True)
    assert len(requests) == 2


def test_load_all(requests: list[str]) -> None:
    loaded = fjc_biographies.load_all()
    assert list(loaded) == [
        'demographics', 'service', 'other_service', 'education', 'career',
        'other_nominations']
    assert len(requests) == 6
    assert list(loaded['other_service'].columns) == [
        'nid', 'sequence', 'judge_name', 'type', 'description']
    roster = fjc_biographies.build_roster(
        loaded['service'], loaded['demographics'], loaded['career'])
    assert len(roster) == len(SERVICE)
    assert roster.loc[roster['nid'] == 104, 'supreme_court_clerk'].all()
