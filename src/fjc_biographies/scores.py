"""Adds scores of judges' ideology to a roster.

Two kinds of scores can be added to a roster made by `parser.build_roster`:

* `add_jcs` adds each appointment's Judicial Common Space score ("jcs"),
  computed by the judicial-common-space package (Epstein, Martin, Segal, and
  Westerland, "The Judicial Common Space," 23 J.L. Econ. & Org. 303 (2007)):
  the NOMINATE score of the judge's home-state senators of the president's
  party, or else of the president, and for a justice, the justice's
  Martin-Quinn score in the first term of the appointment, put on the same
  scale.
* `add_martin_quinn` adds the Martin-Quinn scores of the justices of the
  Supreme Court, which are estimated from their votes in each term
  (https://mqscores.wustl.edu): for each appointment to the Supreme Court,
  the scores of its first and last terms, their mean, and the number of
  terms. `martin_quinn_terms` returns every justice's score in every term.

The scores come from files that are downloaded when they are needed, into the
data folder of judicial-common-space (see
`judicial_common_space.utilities.data_folder`, which the
`JUDICIAL_COMMON_SPACE_DATA_DIR` environment variable can set, so that
courtpy and judicial-common-space share the downloads). The Martin-Quinn
website sometimes refuses or fails to answer automated requests. Then save
"justices.csv" from https://mqscores.wustl.edu/measures.php in a browser and
pass its path as `martin_quinn`.

Contents:
    add_jcs: adds each appointment's Judicial Common Space score.
    add_martin_quinn: adds the Martin-Quinn scores of each appointment to the
        Supreme Court.
    martin_quinn_terms: returns each justice's Martin-Quinn score in each
        term.

"""

from __future__ import annotations

import logging
import pathlib

import judicial_common_space as jcs
import pandas as pd

from . import downloader

logger = logging.getLogger(__name__)

# The files of Voteview and congress-legislators that the Judicial Common
# Space scores of judges are computed from.
_POLITICS: tuple[str, ...] = (
    'congress', 'legislators_historical', 'legislators_current')
# The columns that `add_martin_quinn` adds, by the summary of an
# appointment's terms that each is.
_MQ_COLUMNS: dict[str, str] = {
    'mq_first': 'first', 'mq_last': 'last', 'mq_mean': 'mean',
    'mq_terms': 'count'}


def add_jcs(
    roster: pd.DataFrame,
    folder: pathlib.Path | str | None = None,
    *,
    scores_folder: pathlib.Path | str | None = None,
    martin_quinn: pathlib.Path | str | None = None,
    update: bool = False) -> pd.DataFrame:
    """Adds each appointment's Judicial Common Space score as "jcs".

    The scores are computed by `judicial_common_space.compute` from the
    FJC's files in the "raw" folder of `folder` (the files that the roster
    was made from), Voteview's NOMINATE scores, the dates of senators'
    service, Wikipedia's lists of circuit judges' duty stations (if they
    can be downloaded), and the justices' Martin-Quinn scores (if they can
    be found).

    Args:
        roster: a roster with a row for each appointment, as
            `parser.build_roster` makes it.
        folder: the data folder with the FJC's files. Defaults to None, in
            which case `downloader.data_folder()` is used.
        scores_folder: the folder for the other files. Defaults to None, in
            which case the data folder of judicial-common-space is used.
        martin_quinn: the path of the file of the justices' Martin-Quinn
            scores. Defaults to None, in which case the file is downloaded
            if it is not there. Without it, the justices have no score.
        update: whether to download the files again even if they are there.
            Defaults to False.

    Returns:
        A new roster with "jcs" after "senate_vote". It is missing for an
            appointment that has no score (as for one by Herbert Hoover,
            whom Voteview does not score).

    Raises:
        KeyError: if `roster` lacks "nid" or "sequence".

    """
    _require(roster, ['nid', 'sequence'])
    files = jcs.sources.paths(scores_folder)
    files.update(_fjc_files(folder, update = update))
    jcs.sources.download(_POLITICS, scores_folder, overwrite = update)
    try:
        jcs.sources.download(
            'duty_stations', scores_folder, overwrite = update)
    except Exception as error:  # noqa: BLE001
        logger.warning(
            'could not download the duty stations of circuit judges, so '
            'judges whose careers show no state have their birth states: %s',
            error)
    try:
        found = _martin_quinn_file(martin_quinn, scores_folder, update = update)
    except RuntimeError as error:
        logger.warning('%s, so the justices have no scores', error)
        found = None
    scored, _ = jcs.compute(files, martin_quinn = found)
    keyed = scored[['nid', 'sequence', 'jcs']].assign(
        nid = pd.to_numeric(scored['nid']).astype('Int64'),
        sequence = pd.to_numeric(scored['sequence']).astype('Int64'),
        jcs = pd.to_numeric(scored['jcs']).astype('Float64'))
    return _insert(roster, keyed, ['jcs'])


def add_martin_quinn(
    roster: pd.DataFrame,
    folder: pathlib.Path | str | None = None,
    *,
    scores_folder: pathlib.Path | str | None = None,
    martin_quinn: pathlib.Path | str | None = None,
    update: bool = False,
    terms: pd.DataFrame | None = None) -> pd.DataFrame:
    """Adds the Martin-Quinn scores of each appointment to the Supreme Court.

    A justice's terms belong to the appointment that the justice served in
    then, so William Rehnquist's terms as Chief Justice are those of his
    second appointment (see `martin_quinn_terms`). The added columns are:

    | Column | Meaning |
    | --- | --- |
    | `mq_first`, `mq_last` | The justice's score in the first and last terms of the appointment. |
    | `mq_mean` | The mean of the justice's scores in the terms of the appointment. |
    | `mq_terms` | The number of terms of the appointment that are scored. |

    They are missing for every other appointment, and for one with no
    scored terms.

    Args:
        roster: a roster with a row for each appointment, as
            `parser.build_roster` makes it.
        folder: the data folder with the FJC's files. Defaults to None, in
            which case `downloader.data_folder()` is used.
        scores_folder: the folder for the file of Martin-Quinn scores.
            Defaults to None, in which case the data folder of
            judicial-common-space is used.
        martin_quinn: the path of the file of the justices' Martin-Quinn
            scores ("justices.csv"). Defaults to None, in which case the file
            is downloaded if it is not there.
        update: whether to download the files again even if they are there.
            Defaults to False.
        terms: the justices' scores in each term, as `martin_quinn_terms`
            returns them. Defaults to None, in which case they are found
            from the files (and the other arguments are not used).

    Returns:
        A new roster with the columns after "senate_vote" (and "jcs", if it
            is there).

    Raises:
        KeyError: if `roster` lacks "nid" or "sequence".
        RuntimeError: if there is no file of Martin-Quinn scores and it
            cannot be downloaded.

    """
    _require(roster, ['nid', 'sequence'])
    if terms is None:
        terms = martin_quinn_terms(
            folder, scores_folder = scores_folder,
            martin_quinn = martin_quinn, update = update)
    terms = terms.dropna(subset = ['nid', 'sequence']).sort_values(
        'term', kind = 'stable')
    grouped = terms.groupby(['nid', 'sequence'])['martin_quinn']
    summary = pd.DataFrame({
        column: grouped.agg(how) for column, how in _MQ_COLUMNS.items()})
    summary = summary.reset_index().astype({
        'nid': 'Int64', 'sequence': 'Int64', 'mq_first': 'Float64',
        'mq_last': 'Float64', 'mq_mean': 'Float64', 'mq_terms': 'Int64'})
    return _insert(roster, summary, list(_MQ_COLUMNS))


def martin_quinn_terms(
    folder: pathlib.Path | str | None = None,
    *,
    scores_folder: pathlib.Path | str | None = None,
    martin_quinn: pathlib.Path | str | None = None,
    update: bool = False) -> pd.DataFrame:
    """Returns each justice's Martin-Quinn score in each term.

    Each justice of the Martin-Quinn scores is found among the FJC's
    appointments to the Supreme Court, and each term is given to the
    justice's appointment that was serving then, by
    `judicial_common_space.scores.justices`.

    Args:
        folder: the data folder with the FJC's files. Defaults to None, in
            which case `downloader.data_folder()` is used.
        scores_folder: the folder for the file of Martin-Quinn scores.
            Defaults to None, in which case the data folder of
            judicial-common-space is used.
        martin_quinn: the path of the file of the justices' Martin-Quinn
            scores ("justices.csv"). Defaults to None, in which case the file
            is downloaded if it is not there.
        update: whether to download the files again even if they are there.
            Defaults to False.

    Returns:
        A table with a row for each justice in each term: "term" (the year
            in which the term began, in October), "justiceName" (the Supreme
            Court Database's name for the justice), "judge" and "nid" (the
            FJC's), "title" and "sequence" (of the justice's appointment),
            "martin_quinn" (the mean of the score's estimates), and "jcs"
            (the score put on the scale of the Judicial Common Space).
            "nid" and "sequence" are missing for a justice who is not found.

    Raises:
        RuntimeError: if there is no file of Martin-Quinn scores and it
            cannot be downloaded.

    """
    files = _fjc_files(folder, update = update)
    path = _martin_quinn_file(martin_quinn, scores_folder, update = update)
    table = jcs.fjc.appointments(files['service'], files['demographics'])
    terms = jcs.scores.justices(
        jcs.politics.justices(path), table, start_year = 0)
    terms = terms.drop(columns = ['jid'], errors = 'ignore')
    return terms.astype({
        'nid': 'Int64', 'sequence': 'Int64', 'martin_quinn': 'Float64',
        'jcs': 'Float64'}).reset_index(drop = True)


""" Private Functions """


def _fjc_files(
    folder: pathlib.Path | str | None,
    *,
    update: bool) -> dict[str, pathlib.Path]:
    """Returns the FJC's files that the scores are computed from.

    Args:
        folder: the data folder, or None for `downloader.data_folder()`.
        update: whether to download the files again even if they are there.

    Returns:
        The path of each file, by what judicial-common-space calls it
            ("service", "demographics", and "career").

    """
    return downloader.download(
        ['service', 'demographics', 'career'], folder, overwrite = update)


def _insert(
    roster: pd.DataFrame,
    scores: pd.DataFrame,
    columns: list[str]) -> pd.DataFrame:
    """Returns a roster with scores of its appointments.

    Args:
        roster: the roster.
        scores: a table with "nid", "sequence", and `columns`, with at most
            one row for each appointment.
        columns: the columns of `scores` to add.

    Returns:
        A new roster with `columns` after "senate_vote" (and any scores that
            were added before), or at the end if there is no "senate_vote".
            A column that the roster has already is replaced.

    """
    kept = roster.drop(columns = [c for c in columns if c in roster.columns])
    keys = kept[['nid', 'sequence']].astype('Int64')
    found = keys.merge(
        scores[['nid', 'sequence', *columns]], on = ['nid', 'sequence'],
        how = 'left', validate = 'many_to_one')
    found.index = kept.index
    order = list(kept.columns)
    after = next(
        (c for c in ('mq_terms', 'jcs', 'senate_vote') if c in order), None)
    place = order.index(after) + 1 if after else len(order)
    return pd.concat(
        [kept.iloc[:, :place], found[columns], kept.iloc[:, place:]], axis = 1)


def _martin_quinn_file(
    path: pathlib.Path | str | None,
    scores_folder: pathlib.Path | str | None,
    *,
    update: bool) -> pathlib.Path:
    """Returns the file of the justices' Martin-Quinn scores.

    Args:
        path: the path of the file, or None to download it if it is not in
            the data folder of judicial-common-space (or `scores_folder`).
        scores_folder: the folder for the file, or None.
        update: whether to download the file again even if it is there.

    Returns:
        The path of the file. If it cannot be downloaded again, an older
            copy is used, with a warning.

    Raises:
        FileNotFoundError: if `path` names a file that does not exist.
        RuntimeError: if there is no file and it cannot be downloaded.

    """
    if path is not None:
        named = pathlib.Path(path).expanduser()
        if not named.is_file():
            message = f'there is no file of Martin-Quinn scores at {named}'
            raise FileNotFoundError(message)
        return named
    saved: pathlib.Path = jcs.sources.paths(scores_folder)['martin_quinn']
    try:
        jcs.sources.download('martin_quinn', scores_folder, overwrite = update)
    except Exception as error:
        if not saved.is_file():
            message = (
                f'could not download the Martin-Quinn scores ({error}): save '
                f'"justices.csv" from {jcs.options._MQ_PAGE} in a browser '
                f'and pass its path as `martin_quinn` (or --martin-quinn)')
            raise RuntimeError(message) from error
        logger.warning(
            'could not download the Martin-Quinn scores, so the copy at %s '
            'is used: %s', saved, error)
    return saved


def _require(roster: pd.DataFrame, columns: list[str]) -> None:
    """Raises an error if a roster lacks columns.

    Args:
        roster: the roster.
        columns: names of the columns that are needed.

    Raises:
        KeyError: if a column is missing.

    """
    missing = [c for c in columns if c not in roster.columns]
    if missing:
        message = (
            f'the roster needs the columns {missing} to add scores: make it '
            f'with `build_roster`')
        raise KeyError(message)
