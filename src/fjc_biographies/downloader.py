"""Downloads the FJC's Biographical Directory of Article III Federal Judges.

The Federal Judicial Center exports its directory every night as six CSV
files, one for each category of information about the judges (see
https://www.fjc.gov/history/judges/biographical-directory-article-iii-federal-judges-export).
They need no account and are a few megabytes together. They are saved under
their FJC names in the "raw" folder of the data folder:

    data_folder/
    └── raw/    demographics.csv, federal-judicial-service.csv, ...

Contents:
    data_folder: returns the folder where the files are kept.
    download: downloads the FJC's files.
    raw_folder: returns the folder of the downloaded files.

"""

from __future__ import annotations

import logging
import os
import pathlib
import shutil
import sys
import urllib.parse
import urllib.request
from collections.abc import Iterable
from typing import Any

from . import options

logger = logging.getLogger(__name__)


def data_folder() -> pathlib.Path:
    """Returns the folder where the files are kept.

    The folder is the one named by the `FJC_BIOGRAPHIES_DATA_DIR` environment
    variable, if it is set. Otherwise, when fjc_biographies runs from its
    repository, it is `options._DATA_FOLDER`: "data/courts/fjc_biographies"
    two folders above the repository, beside the folder of code projects
    (where courtpy and fjc-idb keep their files as well). When fjc_biographies
    is installed as a package, it is "fjc_biographies" in the user's local
    application data folder on Windows ("%LOCALAPPDATA%"), or in
    "~/.local/share" (or "$XDG_DATA_HOME") on other systems.

    Returns:
        The path of the folder. It is not created.

    """
    named = os.environ.get(options._ENV_DATA)
    if named:
        return pathlib.Path(named).expanduser()
    if (pathlib.Path(__file__).parents[2] / 'pyproject.toml').is_file():
        return options._DATA_FOLDER
    if sys.platform == 'win32':
        base = (
            os.environ.get('LOCALAPPDATA')
            or pathlib.Path.home() / 'AppData' / 'Local')
        return pathlib.Path(base) / 'fjc_biographies'
    base = (
        os.environ.get('XDG_DATA_HOME')
        or pathlib.Path.home() / '.local' / 'share')
    return pathlib.Path(base) / 'fjc_biographies'


def download(
    categories: Iterable[str] | str | None = None,
    folder: pathlib.Path | str | None = None,
    *,
    overwrite: bool = False) -> dict[str, pathlib.Path]:
    """Downloads the FJC's files of the directory.

    A file that was downloaded before is skipped unless `overwrite` is True.
    The FJC adds new judges and corrects its data as it goes, so overwrite
    the files to get the latest data.

    Args:
        categories: the categories to download ("demographics", "service",
            "other_service", "education", "career", and "other_nominations").
            Defaults to None, in which case every category is downloaded.
        folder: the data folder, whose "raw" folder the files are saved in.
            Defaults to None, in which case `data_folder()` is used.
        overwrite: whether to download a file that is already there. Defaults
            to False.

    Returns:
        The path of each file, by its category.

    Raises:
        ValueError: if a category is not one of the FJC's.

    Examples:
        >>> import fjc_biographies
        >>> fjc_biographies.download(['service', 'demographics'])  # doctest: +SKIP

    """
    chosen = _categories(categories)
    raw = raw_folder(folder)
    paths = {}
    for category in chosen:
        path = raw / options._CATEGORIES[category]
        if overwrite or not path.is_file():
            _save(options._FJC_URL + path.name, path)
        else:
            logger.info('Skipped %s, which already exists.', path.name)
        paths[category] = path
    return paths


def raw_folder(folder: pathlib.Path | str | None = None) -> pathlib.Path:
    """Returns the folder of the downloaded files.

    Args:
        folder: the data folder. Defaults to None, in which case
            `data_folder()` is used.

    Returns:
        The "raw" folder of the data folder. It is not created.

    """
    root = pathlib.Path(folder).expanduser() if folder else data_folder()
    return root / 'raw'


""" Private Functions """


def _categories(categories: Iterable[str] | str | None) -> list[str]:
    """Returns the categories that are named, in order and without repeats.

    Args:
        categories: names of categories, or None for every category.

    Returns:
        The names.

    Raises:
        ValueError: if a name is not one of the FJC's categories.

    """
    if categories is None:
        return list(options._CATEGORIES)
    if isinstance(categories, str):
        categories = [categories]
    chosen = list(dict.fromkeys(categories))
    unknown = [name for name in chosen if name not in options._CATEGORIES]
    if unknown:
        message = (
            f'{unknown} are not categories of the directory, which are '
            f'{list(options._CATEGORIES)}')
        raise ValueError(message)
    return chosen


def _open(url: str) -> Any:
    """Opens a web address with the fjc_biographies user agent.

    Args:
        url: the web address.

    Returns:
        The response to the request.

    Raises:
        ValueError: if `url` is not an https address.

    """
    if urllib.parse.urlparse(url).scheme != 'https':
        message = f'Only https addresses can be downloaded, not {url}.'
        raise ValueError(message)
    request = urllib.request.Request(  # noqa: S310
        url, headers = {'User-Agent': options._USER_AGENT})
    return urllib.request.urlopen(  # noqa: S310
        request, timeout = options._TIMEOUT)


def _save(url: str, path: pathlib.Path) -> pathlib.Path:
    """Downloads a file.

    The file is written under a temporary name and renamed when complete, so
    an interrupted download does not leave a partial file behind.

    Args:
        url: the address of the file.
        path: where to save it. Its folder is created if needed.

    Returns:
        `path`.

    """
    path.parent.mkdir(parents = True, exist_ok = True)
    partial = path.with_name(f'{path.name}.part')
    logger.info('Downloading %s.', path.name)
    try:
        with _open(url) as response, partial.open('wb') as file:
            shutil.copyfileobj(response, file)
        partial.replace(path)
    finally:
        partial.unlink(missing_ok = True)
    return path
