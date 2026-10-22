"""Default settings for downloading and parsing the FJC's judge biographies.

These are module-level constants so that a project built on `fjc_biographies`
can change them before they are used (for example,
`fjc_biographies.options._TIMEOUT = 600` to wait longer for the FJC website).

Contents:
    _ABA_RATINGS: the number for each rating of the American Bar Association.
    _APPEALS_CIRCUITS: the number of each court of appeals' circuit, by the
        words that name it.
    _CATEGORIES: the FJC's files of the directory, by what `fjc_biographies`
        calls each.
    _COLUMN_NAMES: names for the columns whose names are not made the usual
        way (see `parser.tidy`).
    _DATA_FOLDER: the data folder when fjc_biographies runs from its
        repository.
    _DISTRICT_CIRCUITS: the number of the circuit of each state or territory
        with a district court.
    _ENV_DATA: environment variable that can name the data folder.
    _EXPORT_URL: address of the page that links to the FJC's files.
    _FJC_URL: address of the folder with the FJC's files.
    _PARTIES: the number for each party of an appointing president.
    _TIMEOUT: seconds to wait for the FJC website before giving up.
    _USER_AGENT: how fjc_biographies identifies itself to servers.

"""

from __future__ import annotations

import pathlib

_ABA_RATINGS: dict[str, int] = {
    'Exceptionally Well Qualified': 4,
    'Well Qualified': 3,
    'Qualified': 2,
    'Not Qualified': 1,
    'Not Qualified By Reason of Age': 1}
_APPEALS_CIRCUITS: dict[str, int] = {
    'First': 1, 'Second': 2, 'Third': 3, 'Fourth': 4, 'Fifth': 5, 'Sixth': 6,
    'Seventh': 7, 'Eighth': 8, 'Ninth': 9, 'Tenth': 10, 'Eleventh': 11,
    'District of Columbia': 12, 'Federal': 13}
# The files of the Biographical Directory of Article III Federal Judges that
# are organized by category, in the order of the FJC's export page.
_CATEGORIES: dict[str, str] = {
    'demographics': 'demographics.csv',
    'service': 'federal-judicial-service.csv',
    'other_service': 'other-federal-judicial-service.csv',
    'education': 'education.csv',
    'career': 'professional-career.csv',
    'other_nominations': 'other-nominations-recess.csv'}
_COLUMN_NAMES: dict[str, str] = {
    'ayes/nays': 'ayes_nays',
    '2nd service as chief judge, begin': 'second_chief_judge_begin',
    '2nd service as chief judge, end': 'second_chief_judge_end',
    'service as chief judge, begin': 'chief_judge_begin',
    'service as chief judge, end': 'chief_judge_end',
    'other federal judicial service': 'description',
    'other nominations/recess appointments': 'description',
    'professional career': 'position',
    'termination': 'termination_reason'}
# "data/courts/fjc_biographies" two folders above the repository (beside the
# folder of code projects), where courtpy and fjc-idb keep their data too.
_DATA_FOLDER: pathlib.Path = (
    pathlib.Path(__file__).parents[4] / 'data' / 'courts' / 'fjc_biographies')
# The circuits that the states and territories are in now (12 for the
# District of Columbia).
_DISTRICT_CIRCUITS: dict[str, int] = {
    'Maine': 1, 'Massachusetts': 1, 'New Hampshire': 1, 'Puerto Rico': 1,
    'Rhode Island': 1,
    'Connecticut': 2, 'New York': 2, 'Vermont': 2,
    'Delaware': 3, 'New Jersey': 3, 'Pennsylvania': 3, 'Virgin Islands': 3,
    'Maryland': 4, 'North Carolina': 4, 'South Carolina': 4, 'Virginia': 4,
    'West Virginia': 4,
    'Canal Zone': 5, 'Louisiana': 5, 'Mississippi': 5, 'Texas': 5,
    'Kentucky': 6, 'Michigan': 6, 'Ohio': 6, 'Tennessee': 6,
    'Illinois': 7, 'Indiana': 7, 'Wisconsin': 7,
    'Arkansas': 8, 'Iowa': 8, 'Minnesota': 8, 'Missouri': 8, 'Nebraska': 8,
    'North Dakota': 8, 'South Dakota': 8,
    'Alaska': 9, 'Arizona': 9, 'California': 9, 'Guam': 9, 'Hawaii': 9,
    'Idaho': 9, 'Montana': 9, 'Nevada': 9, 'Northern Mariana Islands': 9,
    'Oregon': 9, 'Washington': 9,
    'Colorado': 10, 'Kansas': 10, 'New Mexico': 10, 'Oklahoma': 10,
    'Utah': 10, 'Wyoming': 10,
    'Alabama': 11, 'Florida': 11, 'Georgia': 11,
    'Columbia': 12}
_ENV_DATA: str = 'FJC_BIOGRAPHIES_DATA_DIR'
_EXPORT_URL: str = (
    'https://www.fjc.gov/history/judges/'
    'biographical-directory-article-iii-federal-judges-export')
_FJC_URL: str = 'https://www.fjc.gov/sites/default/files/history/'
_PARTIES: dict[str, int] = {'Democratic': -1, 'Republican': 1}
_TIMEOUT: int = 300
_USER_AGENT: str = (
    'fjc_biographies (+https://github.com/WithPrecedent/fjc_biographies)')
