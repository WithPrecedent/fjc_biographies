# Changelog

All notable changes to this project will be documented in this file.

<!-- insertion marker -->

## 0.0.1

* Downloads the six files of the FJC's Biographical Directory of Article III
  Federal Judges, parses them into tidy tables, and builds a roster of each
  judge's service on each court (taken from `courtpy.judges.build_roster`).
* Makes fields from judges' professional careers with courtpy's rules
  engine and its "judges" rulebook (`instructions/judges.csv`), or a
  rulebook of the user's own (`rulebook` and `--rulebook`).
* Adds the `fjc-biographies` command.
