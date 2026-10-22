"""Command line interface for downloading and exporting the FJC's biographies.

Examples:
    python -m fjc_biographies
    fjc-biographies --update
    fjc-biographies --rulebook my_careers.csv
    fjc-biographies --jcs --martin-quinn
    fjc-biographies --martin-quinn ~/Downloads/justices.csv
    fjc-biographies --download-only --data-folder ~/data/fjc

"""

from __future__ import annotations

import argparse
import logging
import time
from collections.abc import Sequence

from . import downloader
from . import main as biographies

logger = logging.getLogger(__name__)


def main(arguments: Sequence[str] | None = None) -> None:
    """Downloads and exports the FJC's files as the command line arguments say.

    Args:
        arguments: the command line arguments. Defaults to None, in which case
            the arguments passed to the program are used.

    """
    parsed = _get_parser().parse_args(arguments)
    logging.basicConfig(level = logging.INFO, format = '%(message)s')
    started = time.time()
    if parsed.download_only:
        files = downloader.download(
            folder = parsed.data_folder, overwrite = parsed.update)
        logger.info(
            'Downloaded %s files in %.0fs.', len(files), time.time() - started)
        return
    files = biographies.run(
        parsed.data_folder, update = parsed.update, rulebook = parsed.rulebook,
        jcs = parsed.jcs, martin_quinn = parsed.martin_quinn,
        scores_folder = parsed.scores_folder)
    logger.info(
        'Exported %s tables to %s in %.0fs.',
        len(files), next(iter(files.values())).parent, time.time() - started)


def _get_parser() -> argparse.ArgumentParser:
    """Returns the parser for the command line arguments.

    Returns:
        The command line parser.

    """
    parser = argparse.ArgumentParser(
        prog = 'fjc-biographies',
        description = (
            "Download the FJC's Biographical Directory of Article III Federal "
            'Judges and export tidy CSV files and a roster of judges, by '
            'appointment and by judge.'))
    parser.add_argument(
        '--data-folder',
        default = None,
        help = (
            'the folder for the downloaded and exported files (default: '
            f'{downloader.data_folder()})'))
    parser.add_argument(
        '--update',
        action = 'store_true',
        help = (
            'download the files again even if they were downloaded before, '
            'to get the judges and corrections the FJC has added since'))
    parser.add_argument(
        '--rulebook',
        default = 'judges',
        help = (
            "a CSV file of rules that make the roster's fields from judges' "
            'careers, or the name of a built-in rulebook (default: '
            '%(default)s)'))
    parser.add_argument(
        '--jcs',
        action = 'store_true',
        help = (
            "add each appointment's Judicial Common Space score, computed by "
            'the judicial-common-space package'))
    parser.add_argument(
        '--martin-quinn',
        nargs = '?',
        const = True,
        default = False,
        metavar = 'PATH',
        help = (
            "add the justices' Martin-Quinn scores and export their scores in "
            'each term, downloading them, or from PATH (a "justices.csv" saved '
            'from https://mqscores.wustl.edu/measures.php)'))
    parser.add_argument(
        '--scores-folder',
        default = None,
        help = (
            'the folder for the files that the scores come from (default: '
            "the judicial-common-space package's data folder)"))
    parser.add_argument(
        '--download-only',
        action = 'store_true',
        help = 'download the files without exporting them')
    return parser


if __name__ == '__main__':
    main()
