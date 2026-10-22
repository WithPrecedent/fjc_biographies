"""Tests for adding Judicial Common Space and Martin-Quinn scores."""

from __future__ import annotations

import logging
import pathlib
from typing import Any

import judicial_common_space as jcs
import pandas as pd
import pytest
from conftest import SERVICE, tables

import fjc_biographies
from fjc_biographies import __main__ as cli

MQ_COLUMNS = ['mq_first', 'mq_last', 'mq_mean', 'mq_terms']
# Invented Martin-Quinn scores in the layout of "justices.csv": John Marsh
# (the invented justice, 112) in three terms, and a justice the FJC lacks.
MARTIN_QUINN = (
    'term,justice,justiceName,post_mn,post_sd\n'
    '1803,1,JMarsh,1.5,0.2\n'
    '1801,1,JMarsh,0.5,0.2\n'
    '1802,1,JMarsh,1.0,0.2\n'
    '1802,2,XNobody,-2.0,0.3\n')


@pytest.fixture
def martin_quinn(tmp_path: pathlib.Path) -> pathlib.Path:
    """Returns the path of a file of invented Martin-Quinn scores."""
    path = tmp_path / 'justices.csv'
    path.write_text(MARTIN_QUINN, encoding = 'utf-8')
    return path


@pytest.fixture
def roster() -> pd.DataFrame:
    """Returns the roster of the invented judges."""
    files = tables()
    return fjc_biographies.build_roster(
        files['service'], files['demographics'], files['career'])


@pytest.fixture
def computed(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Replaces judicial-common-space's computation and its downloads."""
    calls: dict[str, Any] = {'downloads': []}

    def download(kinds: Any = None, folder: Any = None, *, overwrite: bool = False, **kwargs: Any) -> dict:
        calls['downloads'].append((kinds, overwrite))
        if kinds in ('duty_stations', 'martin_quinn'):
            message = f'{kinds} cannot be reached'
            raise OSError(message)
        return {}

    def compute(files: dict[str, pathlib.Path], **kwargs: Any) -> tuple[pd.DataFrame, pd.DataFrame]:
        calls['files'] = files
        calls['martin_quinn'] = kwargs.get('martin_quinn')
        # A score for each appointment but the second of judge 107, with
        # the numbers as judicial-common-space has them.
        scored = pd.DataFrame(
            [(nid, sequence, nid / 1000) for nid, sequence, *_ in SERVICE
             if (nid, sequence) != (107, 2)],
            columns = ['nid', 'sequence', 'jcs'])
        return scored, pd.DataFrame()

    monkeypatch.setattr(jcs.sources, 'download', download)
    monkeypatch.setattr(jcs, 'compute', compute)
    return calls


def test_martin_quinn_terms(requests: list[str], martin_quinn: pathlib.Path) -> None:
    terms = fjc_biographies.martin_quinn_terms(martin_quinn = martin_quinn)
    assert len(terms) == 4
    marsh = terms[terms['justiceName'] == 'JMarsh'].sort_values('term')
    assert list(marsh['nid']) == [112] * 3
    assert list(marsh['sequence']) == [1] * 3
    assert list(marsh['martin_quinn']) == [0.5, 1.0, 1.5]
    # The scores are put on the scale of the Judicial Common Space too.
    assert marsh['jcs'].between(-1, 1).all()
    # A justice whom the FJC's files lack has no numbers.
    nobody = terms[terms['justiceName'] == 'XNobody'].iloc[0]
    assert pd.isna(nobody['nid']) and pd.isna(nobody['sequence'])
    assert terms['nid'].dtype == 'Int64'
    # The FJC's files are downloaded if they are not there.
    assert any(url.endswith('federal-judicial-service.csv') for url in requests)


def test_add_martin_quinn(requests: list[str], roster: pd.DataFrame, martin_quinn: pathlib.Path) -> None:
    scored = fjc_biographies.add_martin_quinn(roster, martin_quinn = martin_quinn)
    assert len(scored) == len(roster)
    columns = list(scored.columns)
    place = columns.index('senate_vote') + 1
    assert columns[place:place + 4] == MQ_COLUMNS
    marsh = scored[scored['nid'] == 112].iloc[0]
    # The first and last terms are by year, not by the file's order.
    assert (marsh['mq_first'], marsh['mq_last'], marsh['mq_mean'], marsh['mq_terms']) == (0.5, 1.5, 1.0, 3)
    # Only appointments to the Supreme Court have scores.
    assert scored.loc[scored['nid'] != 112, MQ_COLUMNS].isna().all(axis = None)
    assert scored['mq_terms'].dtype == 'Int64'
    assert scored['mq_mean'].dtype == 'Float64'
    # The roster is not changed, and adding the scores again replaces them.
    assert 'mq_first' not in roster.columns
    again = fjc_biographies.add_martin_quinn(scored, martin_quinn = martin_quinn)
    assert list(again.columns) == columns


def test_martin_quinn_by_judge(requests: list[str], roster: pd.DataFrame, martin_quinn: pathlib.Path) -> None:
    scored = fjc_biographies.add_martin_quinn(roster, martin_quinn = martin_quinn)
    judges = fjc_biographies.roster_by_judge(scored).set_index('nid')
    # The scores describe an appointment, so they are numbered.
    assert judges.loc[112, 'mq_mean_1'] == 1.0
    assert 'mq_mean' not in judges.columns
    assert pd.isna(judges.loc[107, 'mq_mean_2'])


def test_martin_quinn_file_is_needed(
    requests: list[str],
    roster: pd.DataFrame,
    no_score_downloads: list[Any],
    caplog: pytest.LogCaptureFixture) -> None:
    # Without a file or a download, the error says how to get the file.
    with pytest.raises(RuntimeError, match = 'justices.csv'):
        fjc_biographies.add_martin_quinn(roster)
    assert no_score_downloads[-1][0] == 'martin_quinn'
    with pytest.raises(FileNotFoundError, match = 'no file of Martin-Quinn'):
        fjc_biographies.add_martin_quinn(roster, martin_quinn = 'no_such_file.csv')
    # A copy that was downloaded before is used when the download fails.
    saved = jcs.sources.paths()['martin_quinn']
    saved.parent.mkdir(parents = True)
    saved.write_text(MARTIN_QUINN, encoding = 'utf-8')
    with caplog.at_level(logging.WARNING):
        scored = fjc_biographies.add_martin_quinn(roster, update = True)
    assert 'copy' in caplog.text
    assert no_score_downloads[-1] == ('martin_quinn', None, True)
    assert scored.loc[scored['nid'] == 112, 'mq_terms'].iloc[0] == 3


def test_add_jcs(requests: list[str], roster: pd.DataFrame, computed: dict[str, Any], data_folder: pathlib.Path) -> None:
    scored = fjc_biographies.add_jcs(roster)
    # The scores are computed from the FJC's files that the roster was made
    # from, and the files of politics are downloaded if they are missing.
    assert calls_files(computed) == data_folder / 'raw'
    assert computed['downloads'][0] == (('congress', 'legislators_historical', 'legislators_current'), False)
    # Without duty stations or Martin-Quinn scores, the scores are computed
    # anyway (and the justices have none).
    assert [kinds for kinds, _ in computed['downloads']][1:] == ['duty_stations', 'martin_quinn']
    assert computed['martin_quinn'] is None
    columns = list(scored.columns)
    assert columns[columns.index('senate_vote') + 1] == 'jcs'
    assert scored['jcs'].dtype == 'Float64'
    by_appointment = scored.set_index(['nid', 'sequence'])['jcs']
    assert by_appointment[(101, 1)] == pytest.approx(0.101)
    assert by_appointment[(107, 1)] == pytest.approx(0.107)
    # An appointment without a score has a missing one.
    assert pd.isna(by_appointment[(107, 2)])


def test_add_jcs_options(
    requests: list[str],
    roster: pd.DataFrame,
    computed: dict[str, Any],
    martin_quinn: pathlib.Path) -> None:
    fjc_biographies.add_jcs(roster, martin_quinn = martin_quinn, update = True)
    # A file of Martin-Quinn scores is passed on, and is not downloaded.
    assert computed['martin_quinn'] == martin_quinn
    assert [kinds for kinds, _ in computed['downloads']] == [
        ('congress', 'legislators_historical', 'legislators_current'), 'duty_stations']
    assert all(overwrite for _, overwrite in computed['downloads'])


def test_both_scores(requests: list[str], roster: pd.DataFrame, computed: dict[str, Any], martin_quinn: pathlib.Path) -> None:
    scored = fjc_biographies.add_martin_quinn(
        fjc_biographies.add_jcs(roster), martin_quinn = martin_quinn)
    columns = list(scored.columns)
    place = columns.index('senate_vote') + 1
    assert columns[place:place + 5] == ['jcs', *MQ_COLUMNS]


def test_scores_need_a_roster() -> None:
    table = pd.DataFrame({'nid': [101]})
    with pytest.raises(KeyError, match = 'sequence'):
        fjc_biographies.add_jcs(table)
    with pytest.raises(KeyError, match = 'build_roster'):
        fjc_biographies.add_martin_quinn(table)


def test_run_with_scores(
    requests: list[str],
    computed: dict[str, Any],
    martin_quinn: pathlib.Path,
    tmp_path: pathlib.Path) -> None:
    paths = fjc_biographies.run(tmp_path / 'out', jcs = True, martin_quinn = martin_quinn)
    assert paths['martin_quinn_terms'] == tmp_path / 'out' / 'martin_quinn_terms.csv'
    assert len(pd.read_csv(paths['martin_quinn_terms'])) == 4
    roster = pd.read_csv(paths['roster_by_appointment'])
    assert {'jcs', *MQ_COLUMNS} <= set(roster.columns)
    judges = pd.read_csv(paths['roster_by_judge'])
    assert {'jcs_1', 'mq_mean_1', 'jcs_2'} <= set(judges.columns)
    # The scores are optional.
    plain = fjc_biographies.run(tmp_path / 'plain')
    assert 'martin_quinn_terms' not in plain
    assert 'jcs' not in pd.read_csv(plain['roster_by_appointment']).columns


def test_cli_with_scores(
    requests: list[str],
    computed: dict[str, Any],
    martin_quinn: pathlib.Path,
    tmp_path: pathlib.Path) -> None:
    cli.main([
        '--data-folder', str(tmp_path / 'out'), '--jcs', '--martin-quinn',
        str(martin_quinn), '--scores-folder', str(tmp_path / 'scores')])
    roster = pd.read_csv(tmp_path / 'out' / 'roster_by_appointment.csv')
    assert roster.loc[roster['nid'] == 112, 'mq_terms'].iloc[0] == 3
    assert roster['jcs'].notna().any()
    assert computed['martin_quinn'] == martin_quinn


def calls_files(computed: dict[str, Any]) -> pathlib.Path:
    """Returns the folder of the FJC's files that the scores were computed from."""
    files = computed['files']
    folders = {files[kind].parent for kind in ('service', 'demographics', 'career')}
    assert len(folders) == 1
    return folders.pop()
