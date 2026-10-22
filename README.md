# fjc-biographies

| | |
| --- | --- |
| Version | [![PyPI Latest Release](https://img.shields.io/pypi/v/fjc-biographies.svg?style=for-the-badge&color=cornflowerblue&label=PyPI&logo=PyPI&logoColor=yellow)](https://pypi.org/project/fjc-biographies/) [![GitHub Latest Release](https://img.shields.io/github/v/tag/WithPrecedent/fjc_biographies?style=for-the-badge&color=forestgreen&label=GitHub&logo=github)](https://github.com/WithPrecedent/fjc_biographies/releases) |
| Status | [![Build Status](https://img.shields.io/github/actions/workflow/status/WithPrecedent/fjc_biographies/ci.yml?style=for-the-badge&branch=main&color=cadetblue&label=Tests&logo=pytest)](https://github.com/WithPrecedent/fjc_biographies/actions/workflows/ci.yml?query=branch%3Amain) [![Code Coverage](https://img.shields.io/codecov/c/github/WithPrecedent/fjc_biographies?style=for-the-badge&color=cadetblue&label=Coverage&logo=codecov)](https://app.codecov.io/gh/WithPrecedent/fjc_biographies) [![Development Status](https://img.shields.io/badge/Development-Active-seagreen?style=for-the-badge&logo=git)](https://www.repostatus.org/#active) [![Project Stability](https://img.shields.io/pypi/status/fjc-biographies?style=for-the-badge&logo=pypi&label=Stability&logoColor=yellow)](https://pypi.org/project/fjc-biographies/) |
| Documentation | [![Hosted By](https://img.shields.io/badge/Hosted_by-Github_Pages-blue?style=for-the-badge&color=forestgreen&logo=github)](https://WithPrecedent.github.io/fjc_biographies) |
| Tools | [![Documentation](https://img.shields.io/badge/MkDocs-magenta?style=for-the-badge&color=deepskyblue&logo=markdown&labelColor=gray)](https://squidfunk.github.io/mkdocs-material/) [![Linter](https://img.shields.io/endpoint?style=for-the-badge&url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Type Checker](https://img.shields.io/badge/mypy-steelblue?style=for-the-badge&logo=python&logoColor=white&labelColor=gray)](https://mypy-lang.org/) [![Dependency Manager](https://img.shields.io/badge/uv-mediumpurple?style=for-the-badge&logo=uv&labelColor=gray)](https://docs.astral.sh/uv/) [![Pre-commit](https://img.shields.io/badge/pre--commit-darkolivegreen?style=for-the-badge&logo=pre-commit&logoColor=white&labelColor=gray)](https://pre-commit.com/) [![CI](https://img.shields.io/badge/GitHub_Actions-forestgreen?style=for-the-badge&logo=githubactions&labelColor=gray&logoColor=white)](https://github.com/features/actions) [![Editor Settings](https://img.shields.io/badge/Editor_Config-paleturquoise?style=for-the-badge&logo=editorconfig&labelColor=gray)](https://editorconfig.org/) [![Repository Template](https://img.shields.io/badge/snickerdoodle-bisque?style=for-the-badge&logo=cookiecutter&labelColor=gray)](https://www.github.com/WithPrecedent/snickerdoodle) [![Dependency Maintainer](https://img.shields.io/badge/dependabot-forestgreen?style=for-the-badge&logo=dependabot&logoColor=white&labelColor=gray)](https://github.com/dependabot) |
| Compatibility | [![Compatible Python Versions](https://img.shields.io/pypi/pyversions/fjc-biographies?style=for-the-badge&color=cornflowerblue&label=Python&logo=python&logoColor=yellow)](https://pypi.org/project/fjc-biographies/) [![Linux](https://img.shields.io/badge/Linux-lightseagreen?style=for-the-badge&logo=linux&labelColor=gray&logoColor=white)](https://www.linux.org/) [![MacOS](https://img.shields.io/badge/MacOS-antiquewhite?style=for-the-badge&logo=apple&labelColor=gray)](https://www.apple.com/macos/) [![Windows](https://img.shields.io/badge/Windows-blue?style=for-the-badge)](https://www.microsoft.com/en-us/windows?r=1) |
| Stats | [![PyPI Download Rate (per month)](https://img.shields.io/pypi/dm/fjc-biographies?style=for-the-badge&color=cornflowerblue&label=Downloads%20💾&logo=pypi&logoColor=yellow)](https://pypi.org/project/fjc-biographies/) [![GitHub Stars](https://img.shields.io/github/stars/WithPrecedent/fjc_biographies?style=for-the-badge&color=forestgreen&label=Stars%20⭐&logo=github)](https://github.com/WithPrecedent/fjc_biographies/stargazers) [![GitHub Contributors](https://img.shields.io/github/contributors/WithPrecedent/fjc_biographies?style=for-the-badge&color=forestgreen&label=Contributors%20🙋&logo=github)](https://github.com/WithPrecedent/fjc_biographies/graphs/contributors) [![GitHub Issues](https://img.shields.io/github/issues/WithPrecedent/fjc_biographies?style=for-the-badge&color=forestgreen&label=Issues%20📘&logo=github)](https://github.com/WithPrecedent/fjc_biographies/issues) [![GitHub Forks](https://img.shields.io/github/forks/WithPrecedent/fjc_biographies?style=for-the-badge&color=forestgreen&label=Forks%20🍴&logo=github)](https://github.com/WithPrecedent/fjc_biographies/forks) |
| | |

-----

## What is fjc-biographies?

`fjc-biographies` downloads the Federal Judicial Center's [Biographical
Directory of Article III Federal Judges](https://www.fjc.gov/history/judges/biographical-directory-article-iii-federal-judges-export)
and turns it into tidy tables, including a roster of judges in two formats:
by appointment (a row for each court that each judge has served on) and by
judge (a row for each judge).

## Why use fjc-biographies?

- **One step.** `fjc-biographies` downloads all six of the FJC's files
  (demographics, federal judicial service, other federal judicial service,
  education, professional career, and other nominations) and exports a tidy
  CSV file of each.
- **A roster of judges.** `build_roster` codes what researchers usually want
  to know about each appointment: the circuit, the years of service and
  senior status, the appointing president's party, the ABA rating, the share
  of senators who voted to confirm, whether it was a recess appointment, the
  judge's gender and race, etc.
- **Fields from careers, written in a spreadsheet.** A rulebook (a CSV file
  of regular expressions) makes new fields from each judge's
  employment history. The built-in "judges" rulebook flags whether the judge
  was a prosecutor, public defender, law clerk, Supreme Court clerk,
  solicitor general, or law professor, and your own rulebook can add flags,
  counts, labels, or lists of matches without changing any code.
  The employment history itself stays in the roster as `career`, one
  position per line, so every field can be checked against the text it was
  made from.
- **Names for matching.** Each judge's name is written twelve ways, for
  matching it against opinions and other datasets: first, middle, and last
  names; with the middle initial; without the middle name; each with and
  without the suffix ("Milton Dale Smith, Jr."); and, for the FJC's names
  with letters in square brackets, both with the brackets removed ("Robert
  Lanier Anderson") and with the bracketed letters replaced by a period
  ("R. Lanier Anderson").
- **Ideology scores, if you want them.** `--jcs` adds each appointment's
  Judicial Common Space score, computed by
  [judicial-common-space](https://github.com/WithPrecedent/judicial_common_space),
  and `--martin-quinn` adds the justices'
  [Martin-Quinn scores](https://mqscores.wustl.edu) for each appointment to
  the Supreme Court and exports every justice's score in every term.
- **Reassignments handled.** A judge who was reassigned to another court
  without a new appointment (as when the Eleventh Circuit was divided from
  the Fifth) keeps the president, party, rating, and vote of the judge's last
  appointment.

The roster is the one that [courtpy](https://github.com/WithPrecedent/courtpy)
uses to identify the judges of cases, which this package was taken from.

## Getting started

### Requirements

Python 3.11 or later. The dependencies are `pandas` (3.0 or later), `numpy`,
and [judicial-common-space](https://pypi.org/project/judicial-common-space/)
(0.1.0 or later), which `pip` installs with it.

### Installation

To install `fjc-biographies`, use `pip`:

```sh
pip install fjc-biographies
```

### Usage

From the command line, download the files and export the tidy tables and the
roster:

```sh
fjc-biographies
```

The roster is exported in two formats, as the FJC's own export is:

| File | Rows | Columns |
| --- | --- | --- |
| `roster_by_appointment.csv` | One for each court that each judge has served on | The judge's fields, repeated on each of the judge's rows, and the appointment's fields (`court`, `start_date`, `president`, `party`, ...) |
| `roster_by_judge.csv` | One for each judge | The judge's fields once, `appointments` (how many courts the judge has served on), and each appointment's fields, numbered in the order of the judge's service (`court_1`, `start_date_1`, ..., `court_2`, ...) |

The FJC updates the directory nightly. Add `--update` to download the files
again, `--download-only` to skip exporting, and `--data-folder` to choose
where the files go. By default, they go in `data/courts/fjc_biographies`
beside the folder of the repository, or in the user's application data
folder when the package is installed (set `FJC_BIOGRAPHIES_DATA_DIR` to
choose another).

From Python:

```python
import fjc_biographies

# The tidy table of one file, which is downloaded if it is not there.
service = fjc_biographies.load('service')

# Every file, and the roster made from them.
tables = fjc_biographies.load_all()
roster = fjc_biographies.build_roster(
    tables['service'], tables['demographics'], tables['career'])

# The same roster with a row for each judge.
by_judge = fjc_biographies.roster_by_judge(roster)
```

To make other fields from judges' careers, copy the built-in rulebook
([`judges.csv`](src/fjc_biographies/instructions/judges.csv)), change or add
rules, and name it:

```python
roster = fjc_biographies.build_roster(
    tables['service'], tables['demographics'], tables['career'],
    rulebook = 'my_careers.csv')
careers = fjc_biographies.code_careers(tables['career'], rulebook = 'my_careers.csv')
```

or `fjc-biographies --rulebook my_careers.csv` from the command line. The
columns of a rulebook and the kinds of rules are described in the
[instructions folder](src/fjc_biographies/instructions/README.md).

### Scores

Judicial Common Space and Martin-Quinn scores are optional:

```sh
fjc-biographies --jcs --martin-quinn
```

```python
roster = fjc_biographies.add_jcs(roster)
roster = fjc_biographies.add_martin_quinn(roster)
terms = fjc_biographies.martin_quinn_terms()
```

| Column | Meaning |
| --- | --- |
| `jcs` | The appointment's Judicial Common Space score: the NOMINATE score of the judge's home-state senators of the president's party, or else of the president, and for a justice, the Martin-Quinn score of the appointment's first term on the same scale. |
| `mq_first`, `mq_last`, `mq_mean`, `mq_terms` | For an appointment to the Supreme Court, the justice's Martin-Quinn scores in its first and last terms, their mean, and the number of terms scored. A justice who became Chief Justice has separate scores for each appointment. |

With `--martin-quinn`, `martin_quinn_terms.csv` has every justice's score in
every term, with the FJC's `nid` and the appointment's `sequence`.

The files that the scores come from (Voteview's NOMINATE scores, the dates
of senators' service, and the Martin-Quinn scores) are downloaded into
judicial-common-space's data folder, which `--scores-folder` or the
`JUDICIAL_COMMON_SPACE_DATA_DIR` environment variable can change, so that
courtpy and judicial-common-space share them. The Martin-Quinn website
sometimes refuses or fails to answer automated requests. Then save
`justices.csv` from [its page](https://mqscores.wustl.edu/measures.php) in a
browser and pass its path: `--martin-quinn ~/Downloads/justices.csv`. A copy
that was downloaded before is used if a new one cannot be.

| Category | FJC file | Rows |
| --- | --- | --- |
| `demographics` | `demographics.csv` | One for each judge |
| `service` | `federal-judicial-service.csv` | One for each judge's service on an Article III court |
| `other_service` | `other-federal-judicial-service.csv` | One for each other federal judicial position |
| `education` | `education.csv` | One for each degree |
| `career` | `professional-career.csv` | One for each position in a judge's career |
| `other_nominations` | `other-nominations-recess.csv` | One for each other nomination or recess appointment |

## Contributing

Contributors are always welcome. Feel free to grab an [issue](https://www.github.com/WithPrecedent/fjc_biographies/issues) to work on or make a suggested improvement. If you wish to contribute, please read the [Contribution Guide](https://www.github.com/WithPrecedent/fjc_biographies/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://www.github.com/WithPrecedent/fjc_biographies/blob/main/CODE_OF_CONDUCT.md).

## Similar Projects

* [courtpy](https://github.com/WithPrecedent/courtpy) collects, parses, and
  analyzes court opinions, and matches the judges in them to this roster.
* [fjc-idb](https://github.com/WithPrecedent/fjc_idb) does for the FJC's
  Integrated Database of cases what this package does for its directory of
  judges.

## Acknowledgments

The data are the work of the Federal Judicial Center's Federal Judicial
History Office. The FJC asks that published work cite it as: History of the
Federal Judiciary. http://www.fjc.gov. Web site of the Federal Judicial
Center, Washington, DC.

## Citation

If you use `fjc-biographies` in your research, please cite it. GitHub's
"Cite this repository" button reads the same information from
[`CITATION.cff`](https://www.github.com/WithPrecedent/fjc_biographies/blob/main/CITATION.cff).

```bibtex
@software{yung_fjc_biographies,
  author  = {Yung, Corey Rayburn},
  title   = {fjc-biographies: Downloads and parses the FJC Biographical Directory of Article III Federal Judges},
  version = {0.1.0},
  year    = {2026},
  url     = {https://github.com/WithPrecedent/fjc_biographies},
  license = {Apache-2.0}
}
```

## License

Use of this repository is authorized under the [Apache Software License 2.0](https://www.github.com/WithPrecedent/fjc_biographies/blob/main/LICENSE).
