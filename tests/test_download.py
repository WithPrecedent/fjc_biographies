"""Tests for downloading the FJC's files."""

from __future__ import annotations

import pathlib

import pytest

import fjc_biographies
from fjc_biographies import downloader, options


def test_download(requests: list[str], tmp_path: pathlib.Path) -> None:
    paths = fjc_biographies.download(['service', 'demographics'], tmp_path)
    assert list(paths) == ['service', 'demographics']
    assert paths['service'] == tmp_path / 'raw' / 'federal-judicial-service.csv'
    assert requests == [
        'https://www.fjc.gov/sites/default/files/history/federal-judicial-service.csv',
        'https://www.fjc.gov/sites/default/files/history/demographics.csv']
    assert paths['service'].read_text(encoding = 'utf-8').startswith('"nid"')
    # Files that are there are not downloaded again unless asked.
    fjc_biographies.download('service', tmp_path)
    assert len(requests) == 2
    fjc_biographies.download('service', tmp_path, overwrite = True)
    assert len(requests) == 3


def test_download_everything(requests: list[str], data_folder: pathlib.Path) -> None:
    paths = fjc_biographies.download()
    assert list(paths) == list(options._CATEGORIES)
    assert [path.name for path in paths.values()] == list(options._CATEGORIES.values())
    # The default folder is the data folder.
    assert paths['service'].parent == data_folder / 'raw'
    assert len(requests) == 6


def test_download_unknown_category(requests: list[str]) -> None:
    with pytest.raises(ValueError, match = 'not categories'):
        fjc_biographies.download(['service', 'judges'])
    assert requests == []


def test_failed_download_leaves_no_file(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    def refuse(url: str) -> None:
        raise OSError(f'cannot reach {url}')

    monkeypatch.setattr(downloader, '_open', refuse)
    with pytest.raises(OSError, match = 'cannot reach'):
        fjc_biographies.download('service', tmp_path)
    assert list((tmp_path / 'raw').iterdir()) == []


def test_only_https() -> None:
    with pytest.raises(ValueError, match = 'https'):
        downloader._open('http://www.fjc.gov/sites/default/files/history/judges.csv')


def test_data_folder(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    monkeypatch.setenv(options._ENV_DATA, str(tmp_path / 'named'))
    assert fjc_biographies.data_folder() == tmp_path / 'named'
    # Run from its repository, the data folder is beside the code projects.
    monkeypatch.delenv(options._ENV_DATA)
    assert fjc_biographies.data_folder() == options._DATA_FOLDER
