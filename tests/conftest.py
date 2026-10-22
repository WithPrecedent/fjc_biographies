"""Invented judges in the layout of the FJC's files, and a fake FJC website."""

from __future__ import annotations

import io
import pathlib
from typing import Any

import judicial_common_space as jcs
import pandas as pd
import pytest

from fjc_biographies import downloader, options

FIRST = 'U.S. Court of Appeals for the First Circuit'
NINTH = 'U.S. Court of Appeals for the Ninth Circuit'
APPEALS = 'U.S. Court of Appeals'
DISTRICT = 'U.S. District Court'
# Invented judges, in the layout of the FJC's file of federal judicial
# service: nid, sequence, name, court type, court, president, party, ABA
# rating, recess appointment, vote type, ayes/nays, commission, senior
# status, and termination.
SERVICE = [
    (101, 1, 'Lynch, Mary Ann', APPEALS, FIRST, 'William J. Clinton', 'Democratic', 'Well Qualified', '', 'Voice', '', '1995-03-17', '', ''),
    (102, 1, 'Howard, John Q.', APPEALS, FIRST, 'George W. Bush', 'Republican', 'Qualified', '', 'Roll Call', ' 99/1', '2002-04-23', '', ''),
    (103, 1, 'Thompson, Rita Mae', APPEALS, FIRST, 'Barack Obama', 'Democratic', 'Exceptionally Well Qualified', '', 'Roll Call', ' 98/0', '2010-03-17', '', ''),
    (104, 1, 'Smith, Milton Dale, Jr.', APPEALS, NINTH, 'George W. Bush', 'Republican', 'Well Qualified', '', 'Voice', '', '2006-05-18', '', ''),
    (105, 1, 'Smith, N[orman] Roy', APPEALS, NINTH, 'George W. Bush', 'Republican', '', '', 'Roll Call', ' 94/0', '2007-03-19', '', ''),
    (106, 1, 'Woods, Dana Paul', DISTRICT, 'U.S. District Court for the District of Massachusetts', 'Ronald Reagan', 'Republican', 'Not Qualified', '', 'Voice', '', '1986-06-16', '2015-06-01', ''),
    (107, 2, 'Stone, Nora H.', APPEALS, FIRST, 'George H.W. Bush', 'Republican', 'Well Qualified', '', 'Voice', '', '1992-04-30', '2001-04-16', ''),
    (107, 1, 'Stone, Nora H.', DISTRICT, 'U.S. District Court for the District of New Hampshire', 'George H.W. Bush', 'Republican', 'Qualified', '', 'Voice', '', '1990-04-27', '', '1992-04-30'),
    (108, 1, 'Fields, R[ay] Lanier III', APPEALS, 'U.S. Court of Appeals for the Fifth Circuit', 'Jimmy Carter', 'Democratic', 'Well Qualified', '', 'Roll Call', ' 60/30', '1979-07-13', '', '1981-10-01'),
    (108, 2, 'Fields, R[ay] Lanier III', APPEALS, 'U.S. Court of Appeals for the Eleventh Circuit', 'None (reassignment)', 'None (reassignment)', '', '', '', '', '1981-10-01', '', ''),
    (109, 1, 'Rake, Jed Saul', DISTRICT, 'U.S. District Court for the Southern District of New York', 'William J. Clinton', 'Democratic', 'Well Qualified', '', 'Voice', '', '1996-03-01', '', ''),
    (110, 1, 'Poser, Richard Allen', APPEALS, 'U.S. Court of Appeals for the Seventh Circuit', 'Ronald Reagan', 'Republican', 'Qualified', '', 'Voice', '', '1981-12-01', '', '2017-09-02'),
    (111, 1, 'Gray, Roger L.', APPEALS, 'U.S. Court of Appeals for the Fourth Circuit', 'William J. Clinton', 'Democratic', '', '2000-12-27', 'Unknown', '', '', '', '2001-07-20'),
    (112, 1, 'Marsh, John', 'Supreme Court', 'Supreme Court of the United States', 'John Adams', 'Federalist', '', '', 'Voice', '', '1801-01-31', '', '1835-07-06'),
    (113, 1, 'Ward, Ellen', APPEALS, 'U.S. Court of Appeals for the District of Columbia Circuit', 'Barack Obama', 'Democratic', 'Well Qualified', '', 'Roll Call', ' 53/44', '2013-12-12', '', ''),
    (113, 2, 'Ward, Ellen', APPEALS, 'U.S. Court of Appeals for the Federal Circuit', 'None (reassignment)', 'None (reassignment)', '', '', '', '', '2020-01-02', '', '')]
SERVICE_COLUMNS = [
    'nid', 'Sequence', 'Judge Name', 'Court Type', 'Court Name',
    'Appointing President', 'Party of Appointing President', 'ABA Rating',
    'Recess Appointment Date', 'Senate Vote Type', 'Ayes/Nays',
    'Commission Date', 'Senior Status Date', 'Termination Date']
DEMOGRAPHICS = [
    (101, 'Lynch', 'Mary', 'Ann', '', '1946', 'Female', 'White'),
    (102, 'Howard', 'John', 'Q.', '', '1955', 'Male', 'White'),
    (103, 'Thompson', 'Rita', 'Mae', '', '1951', 'Female', 'African American'),
    (104, 'Smith', 'Milton', 'Dale', 'Jr.', '1942', 'Male', 'White'),
    (105, 'Smith', 'N[orman]', 'Roy', '', '1949', 'Male', 'Hispanic/White'),
    (106, 'Woods', 'Dana', 'Paul', '', '1947', 'Male', 'White'),
    (107, 'Stone', 'Nora', 'H.', '', '1931', 'Female', 'White'),
    (108, 'Fields', 'R[ay]', 'Lanier', 'III', '1936', 'Male', 'White'),
    (109, 'Rake', 'Jed', 'Saul', '', '1943', 'Male', 'White'),
    (110, 'Poser', 'Richard', 'Allen', '', '1939', 'Male', 'White'),
    (111, 'Gray', 'Roger', 'L.', '', '1953', 'Male', 'African American'),
    (112, 'Marsh', 'John', ' ', '', '1755', '', ''),
    (113, 'Ward', 'Ellen', '', '', '1970', 'Declined to Report', 'White')]
DEMOGRAPHICS_COLUMNS = [
    'nid', 'Last Name', 'First Name', 'Middle Name', 'Suffix', 'Birth Year',
    'Gender', 'Race or Ethnicity']
CAREER = [
    (101, 1, 'Law clerk, Hon. A. Judge, U.S. District Court, District of Rhode Island, 1971-1973'),
    (101, 2, 'Assistant attorney general, State of Massachusetts, 1973-1974'),
    (102, 1, 'Assistant U.S. attorney, District of New Hampshire, 1981-1987'),
    (103, 1, 'Assistant public defender, Rhode Island, 1976-1979'),
    (104, 1, 'Law clerk, Hon. B. Justice, Supreme Court of the United States, 1970-1971'),
    (104, 2, 'Professor, University of the West School of Law, 1980-1990'),
    (105, 1, 'Reporter of decisions, Supreme Court of the United States, 1990-1991'),
    (105, 2, 'Law clerk, Hon. C. Judge, U.S. District Court, District of Idaho, 1977-1978'),
    (113, 1, 'Deputy Solicitor General, U.S. Department of Justice, 2009-2013')]
CAREER_COLUMNS = ['nid', 'Sequence', 'Professional Career']


def tables() -> dict[str, pd.DataFrame]:
    """Returns the files of invented judges, as they are read."""
    names = {row[0]: row[2] for row in SERVICE}
    # judicial-common-space reads a few more of the FJC's columns.
    demographics = pd.DataFrame(DEMOGRAPHICS, columns = DEMOGRAPHICS_COLUMNS).assign(
        jid = lambda table: table['nid'], **{'Birth State': ''})
    service = pd.DataFrame(SERVICE, columns = SERVICE_COLUMNS).assign(**{
        'Appointment Title': 'Judge', 'Nomination Date': '', 'Confirmation Date': ''})
    return {
        'demographics': demographics,
        'service': service,
        'other_service': pd.DataFrame(
            [(101, 1, names[101], 'U.S. Magistrate Judge', 'U.S. Magistrate Judge, District of Maine, 1990-1995', '', '')],
            columns = ['nid', 'Sequence', 'Judge Name', 'Type', 'Other Federal Judicial Service', '', ' ']),
        'education': pd.DataFrame(
            [(101, 1, names[101], 'Harvard Law School', 'J.D.', '1971'),
             (102, 1, names[102], 'Yale Law School', '', '')],
            columns = ['nid', 'Sequence', 'Judge Name', 'School', 'Degree', 'Degree Year']),
        'career': pd.DataFrame(CAREER, columns = CAREER_COLUMNS),
        'other_nominations': pd.DataFrame(
            [(103, 1, names[103], 'Nominated to U.S. Court of Appeals for the First Circuit, May 1, 2008; no Senate vote')],
            columns = ['nid', 'Sequence', 'Judge Name', 'Other Nominations/Recess Appointments'])}


def files() -> dict[str, bytes]:
    """Returns the contents of the FJC's files of invented judges, by name."""
    return {
        options._CATEGORIES[category]: table.to_csv(index = False, quoting = 1).encode()
        for category, table in tables().items()}


@pytest.fixture
def requests(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Replaces web requests with a fake FJC website and records them."""
    requested: list[str] = []
    served = files()

    def fake_open(url: str) -> io.BytesIO:
        requested.append(url)
        return io.BytesIO(served[url.rsplit('/', 1)[-1]])

    monkeypatch.setattr(downloader, '_open', fake_open)
    return requested


@pytest.fixture(autouse = True)
def data_folder(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> pathlib.Path:
    """Keeps the tests' files out of the real data folder."""
    folder = tmp_path / 'data'
    monkeypatch.setenv(options._ENV_DATA, str(folder))
    monkeypatch.setenv('JUDICIAL_COMMON_SPACE_DATA_DIR', str(tmp_path / 'scores'))
    return folder


@pytest.fixture(autouse = True)
def no_score_downloads(monkeypatch: pytest.MonkeyPatch) -> list[tuple[Any, Any, bool]]:
    """Refuses judicial-common-space's downloads, and records them."""
    requested: list[tuple[Any, Any, bool]] = []

    def refuse(kinds: Any = None, folder: Any = None, *, overwrite: bool = False, **kwargs: Any) -> None:
        requested.append((kinds, folder, overwrite))
        message = f'the tests do not download {kinds}'
        raise OSError(message)

    monkeypatch.setattr(jcs.sources, 'download', refuse)
    return requested
