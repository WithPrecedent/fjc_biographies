# Instructions

These CSV files are rulebooks: rules that make new fields from the text of
judges' biographies. `fjc_biographies.code_careers` and
`fjc_biographies.build_roster` apply the "judges" rulebook (`judges.csv`)
unless another is named. The columns of a rulebook and the kinds of rules are
described in the `fjc_biographies.rules` module.

Each rule of `judges.csv` searches the section "career", which is a judge's
professional career from the FJC's file of professional careers, with each
position on its own line. So a rule whose pattern must fit within one
position (such as a clerkship at the Supreme Court) uses ".", which does not
match a line break.

| Variable | Kind | Meaning |
| --- | --- | --- |
| `prosecutor` | flag | A prosecutor's office, federal or state (an attorney general's office is counted, although some of its lawyers do civil work). |
| `public_defender` | flag | A public or federal defender's office. |
| `law_clerk` | flag | A clerkship at any court. |
| `supreme_court_clerk` | flag | A clerkship at the Supreme Court of the United States. |
| `solicitor_general` | flag | The office of a solicitor general, federal or state. |
| `law_professor` | flag | A professorship. |

The file is the same as courtpy's `instructions/judges.csv`, so a rule that is
added or changed in one should be in the other.

To code careers in other ways, copy `judges.csv`, change or add rules (for
example, a `count` rule that counts the positions in private practice), and
pass its path as `rulebook`:

```python
import fjc_biographies

tables = fjc_biographies.load_all()
roster = fjc_biographies.build_roster(
    tables['service'], tables['demographics'], tables['career'],
    rulebook = 'my_careers.csv')
```
