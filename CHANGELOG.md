# Changelog

All notable changes to this project will be documented in this file.

<!-- insertion marker -->

## 0.1.0

* Exports the roster in two formats: by appointment
  (`roster_by_appointment.csv`, which was `roster.csv`) and by judge
  (`roster_by_judge.csv`, made by `roster_by_judge`), and `run` returns them
  as "roster_by_appointment" and "roster_by_judge".
* Keeps each judge's professional career in the roster as `career`, one
  position per line, beside the fields made from it.
* Writes each judge's name in twelve ways for matching (`name_first_middle_last`
  and the rest), with the FJC's bracketed letters removed or replaced by a
  period.
* Adds the FJC's `sequence` of each appointment to the roster.
* Adds optional Judicial Common Space scores (`add_jcs`, `--jcs`), computed
  by judicial-common-space (0.1.0 or later, from PyPI), and the justices'
  Martin-Quinn scores (`add_martin_quinn`, `martin_quinn_terms`,
  `--martin-quinn`).
* The tests save the roster of their invented judges in both formats in
  `tests/output`, to be looked at.
* Adds a citation file and a BibTeX citation in the README.

## 0.0.1

* Downloads the six files of the FJC's Biographical Directory of Article III
  Federal Judges, parses them into tidy tables, and builds a roster of each
  judge's service on each court (taken from `courtpy.judges.build_roster`).
* Makes fields from judges' professional careers with courtpy's rules
  engine and its "judges" rulebook (`instructions/judges.csv`), or a
  rulebook of the user's own (`rulebook` and `--rulebook`).
* Adds the `fjc-biographies` command.
