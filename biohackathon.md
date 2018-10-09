# bio.tools & EDAM drop-in hackathon & discussions

### Representative: Jon Ison

## Community

ELIXIR Tools Platform

## Leads
---
Jon Ison + others tbd

## Background information
The proposal is for (ideally many) representatives of the bio.tools and related projects including EDAM, biotoolsSchema, Tool Information Standards etc. to attend all week to host a running "drop-in" session with each day focused on a specific theme.  Themes will be tailored to delegates but might include 1. bio.tools open development process.  2.  bio.tools critique & bug fix.  3. Planning EDAM 2.0.0.   4. EDAM Formats curation.  5. bio.tools content improvement from an end-user perspective.  6. bio.tools annotation consistency.  7. EDAM coverage of bio.tools.  8. edamMap optimisation.  9. edamBrowse brainstorming. 10. Anything else !

## Focus of each day
Each hakacthon day has a focus, which we'll try to stick to, but will adapt depending upon who turns up on the day.

* **Tue Nov 13** [bio.tools testing, evaluation and optimisation](https://github.com/bio-tools/biotoolsRegistry/blob/master/biohackathon.md#biotools-development)
* **Wed Nov 14** [EDAM development](https://github.com/bio-tools/biotoolsRegistry/blob/master/biohackathon.md#edam-development)
* **Thu Nov 15** [bio.tools workflows](https://github.com/bio-tools/biotoolsRegistry/blob/master/biohackathon.md#biotools-workflows)
* **Fri Nov 16** [everything else](https://github.com/bio-tools/biotoolsRegistry/blob/master/biohackathon.md#everything-else)

## bio.tools development
The purpose is to test, evaluate and optimise the development deployment of bio.tools (https://dev.bio.tools/), changes in which are scheduled to be moved into production (https://bio.tools/) during Dec 3-7.

### Task 1: bio.tools release testing
Currently 28 issues labelled ["done - staged for release"](https://github.com/bio-tools/biotoolsregistry/issues?q=is%3Aissue+is%3Aopen+label%3A%22done+-+staged+for+release%22) are implemented in https://dev.bio.tools.  Before these can be moved into production, we need independent verification that these features and fixes have been satisfactorily implemented.  The task is to work through the ["done - staged for release"](https://github.com/bio-tools/biotoolsregistry/issues?q=is%3Aissue+is%3Aopen+label%3A%22done+-+staged+for+release%22) issues, read the thread, test things are working as advertised, and add a comment to the thread (either reporting things look are OK, or describing outstanding problems).  Once an issue is verified in this way, bio.tools core-dev will attach the ["fix verified"](https://github.com/bio-tools/biotoolsRegistry/labels/fix%20verified) label (having first fixed any issues raised).

### Task 2: bio.tools development priorities
We label issues to reflect their status and priority:
* ["critical priority"](https://github.com/bio-tools/biotoolsRegistry/labels/critical%20priority) : our top priorities, including most of the reported [bugs](https://github.com/bio-tools/biotoolsRegistry/labels/bug)
* ["high priority"](https://github.com/bio-tools/biotoolsRegistry/issues?q=is%3Aissue+is%3Aopen+label%3A%22high+priority%22) : things which bio.tools core-dev consider high priorities; we get to these once ["critical priority"](https://github.com/bio-tools/biotoolsRegistry/labels/critical%20priority) issues are addressed
* ["in progress"](https://github.com/bio-tools/biotoolsRegistry/labels/in%20progress) : things we're working on currently
* ["Dec 18 release"](https://github.com/bio-tools/biotoolsRegistry/milestone/2) : things we're aiming to put into the next production deployment
* ["wontfixsoon"](https://github.com/bio-tools/biotoolsRegistry/labels/wontfixsoon) : things which, for one reason or another (usually lack of developer capacity), we don't anticipate doing soon (that's doesn't imply they're unimportant or bad ideas!)

We want to be sure our priorities reflect those of the community at large.  The task is to review the priorities above and add any comments in the appropriate GitHub thread.  You can also request new features by [creating an issue](https://github.com/bio-tools/biotoolsRegistry/issues/new), but please first [search the list of issues](https://github.com/bio-tools/biotoolsRegistry/issues) as it might already be listed.


Community building and I hope solid technical plans and outcomes in all areas.

Expected audience: 
---

Broadly technical people.
**Expected hacking days**: 4 days

---
## Related works and references
- https://bio.tools/
- https://ifb-elixirfr.github.io/edam-browser/#topic_0091
- https://biit.cs.ut.ee/edammap/

## GitHub or any other public repositories of your FOSS products (if any)

- https://github.com/bio-tools/biotoolsschema
- https://github.com/edamontology/edamontology/
- https://github.com/bio-tools/Tool-Information-Standard
- https://github.com/edamontology/edammap
- https://github.com/IFB-ElixirFr/edam-browser

## Hackers
---
