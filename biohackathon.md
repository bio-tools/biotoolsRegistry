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
* **Thu Nov 15** [subject tbd](https://github.com/bio-tools/biotoolsRegistry/blob/master/biohackathon.md#subject-tbd)
* **Fri Nov 16** [publications](https://github.com/bio-tools/biotoolsRegistry/blob/master/biohackathon.md#publications)

## bio.tools development
*Expected audience*: anyone with an interest in improving bio.tools
*Expected outcome*: improved awareness of & community input on bio.tools near-term plans

The purpose is to test, evaluate and optimise the development deployment of bio.tools (https://dev.bio.tools/), changes in which are scheduled to be moved into production (https://bio.tools/) during Dec 3-7.  The bio.tools core-dev will be on hand to discuss things in person.

### Task 1: bio.tools release testing
Currently 28 issues labelled ["done - staged for release"](https://github.com/bio-tools/biotoolsregistry/issues?q=is%3Aissue+is%3Aopen+label%3A%22done+-+staged+for+release%22) are implemented in https://dev.bio.tools.  Before these can be moved into production, we need independent verification that these features and fixes have been satisfactorily implemented.

The task is to work through the ["done - staged for release"](https://github.com/bio-tools/biotoolsregistry/issues?q=is%3Aissue+is%3Aopen+label%3A%22done+-+staged+for+release%22) issues, read the thread, test things are working as advertised, and add a comment to the thread (either reporting things look are OK, or describing outstanding problems).

Once an issue is verified in this way, bio.tools core-dev will attach the ["fix verified"](https://github.com/bio-tools/biotoolsRegistry/labels/fix%20verified) label (having first fixed any issues raised).

### Task 2: bio.tools development priorities
We label issues to reflect their status and priority:
* ["critical priority"](https://github.com/bio-tools/biotoolsRegistry/labels/critical%20priority) : our top priorities, including most of the reported [bugs](https://github.com/bio-tools/biotoolsRegistry/labels/bug)
* ["high priority"](https://github.com/bio-tools/biotoolsRegistry/issues?q=is%3Aissue+is%3Aopen+label%3A%22high+priority%22) : things which bio.tools core-dev consider high priorities; we get to these once ["critical priority"](https://github.com/bio-tools/biotoolsRegistry/labels/critical%20priority) issues are addressed
* ["in progress"](https://github.com/bio-tools/biotoolsRegistry/labels/in%20progress) : things we're working on currently
* ["Dec 18 release"](https://github.com/bio-tools/biotoolsRegistry/milestone/2) : things we're aiming to put into the next production deployment
* ["wontfixsoon"](https://github.com/bio-tools/biotoolsRegistry/labels/wontfixsoon) : things which, for one reason or another (usually lack of developer capacity), we don't anticipate doing soon (that's doesn't imply they're unimportant or bad ideas!)

We want to be sure our priorities reflect those of the community at large.  The task is to review the priorities above and add any comments in the appropriate GitHub thread.  You can also request new features by [creating an issue](https://github.com/bio-tools/biotoolsRegistry/issues/new), but please first [search the list of issues](https://github.com/bio-tools/biotoolsRegistry/issues) as it might already be listed.

### Task 3: bio.tools open development process
Now that bio.tools is [open source](https://github.com/bio-tools/biotoolsRegistry/blob/master/LICENSE), there is an opportunity for hackers everywhere to contribute to the project.  But first we must define how the community development process will work in practice.  We have emerging [contributor guidelines]() but we want to revise these in light of feedback from potential contributors.

The task is to review the emerging [contributor guidelines]() and provide feedback on these via [GitHub](https://github.com/bio-tools/biotoolsRegistry/issues/new).

### Task 4: bio.tools API testing & optimisation
The latest development deployment of the bio.tools API (https://dev.bio.tools/api/tool) is, we hope, a big improvement on the current version.  It supports a comprehensive [set of parameters](https://biotools.readthedocs.io/en/latest/api_reference_dev.html) that enable precise query over tool function and other metadata.  But before we can move these changes into production, the API needs to be thoroughly tested.  There is also an opportunity to optimise the search behaviour, in light of results of real queries, to ensure it works as anticipated.

The task is to systematically test the API, particulaly the behaviour of the search parameters as documented in the [API Reference]() and [API Usage Guide]().  Please provide feedback on the behaviour / possible improvement of the API via GitHub](https://github.com/bio-tools/biotoolsRegistry/issues/new).  Issues or suggestions on the docs can be reported [here](https://github.com/bio-tools/biotoolsdocs/issues).  The bio.tools core-dev will be on-hand and (hopefully, depending on certain developments being completed in time) will be able to tweak the elastic search parameters during the workshop, allowing for immediate iterative improvements. 


## EDAM development
*Expected audience*: anyone with an interest in improving EDAM, people knowledgeable of bioinformatics data formats
*Expected outcome*: improved EDAM Formats subontology, scoping the desired state of EDAM 2.0

### Task 1 Curation of bioinformatics data formats
The [EDAM Format subontology](http://edamontology.org/format_1915) has potential in systems such as [Galaxy](https://f1000research.com/posters/6-1032) and for [workflow composition](https://doi.org/10.1093/bioinformatics/bty646).  EDAM is close to providing a comprehensive catalogue of the prevalent bioinformatics data formats.  To accomplish this, a significant number of [work](https://github.com/edamontology/edamontology/issues/370) must be completed, including [guidelines](https://edamontologydocs.readthedocs.io/en/latest/editors_guide.html#id12) for EDAM Format curation, which have been under [discussion](https://github.com/edamontology/edamontologyDocs/issues/10).

The task is to work on any aspects of the data format curation listed [here](https://github.com/edamontology/edamontology/issues/370) including:

* addition of miscellaneous new data formats, or changes to existing ones ([issue](https://github.com/edamontology/edamontology/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3A%22concept%2Fterm+request%22+format))
* addition of formats ensuring coverage for Galaxy applications ([issue](https://github.com/edamontology/edamontology/issues/85))
* addition of formats to ensure coverage of ([FAIRSharing](https://fairsharing.org/))

### Task 2 Verification of EDAM Formats subontology
We have guidelines for the development of the EDAM formats subontology:
* [editor guidelines](https://edamontologydocs.readthedocs.io/en/latest/editors_guide.html#id12) when modifying EDAM; adding or changing concepts, concept metadata, crosslinking, etc.
* [developer guidelines](https://edamontologydocs.readthedocs.io/en/latest/developers_guide.html#adding-concepts) about the technical process

To develop EDAM Format subontology into a rigorous catalogue, we must ensure the guidelines are followed.

The task is to develop tooling that checks compliance of EDAM to the guidelines above, and generate a human-readable report that can be acted on.
  

### Task 3 Towards EDAM 2.0 (discussion & planning)
It is over 5 years since an [article](https://doi.org/10.1093/bioinformatics/btt113) describing EDAM was published in Bioinformatics.  Since then, there have been 18 new releases (currently EDAM 1.21), with many additions and improvements.  Soon, we hope to release EDAM 2.0 implementing a set of features representing a step forward in value and quality over 1.* releases.

The task (working as a group, or alone) is to enumerate; what are the desirable properties of EDAM 2.0?  We will enumerate these properties in this [issue](https://github.com/edamontology/edamontology/issues/376), creating other issues as needed for finer-grained information.




* cleaning up the connection between EDAM Formats and Data subontologies ([issue](https://github.com/edamontology/edamontology/issues/283), see also [issue](https://github.com/edamontology/edamontology/issues/287))
* 

## Subject tbd
The topic of the fourth day will be decided upon during the hackathon, depending upon interest and conversations in the first three days.


## Publications

There are many developments concerning or involving bio.tools or EDAM which are at various stages of development and - with a little more effort - can be finished off and written up for publication.  These include (but are not limited to):

* blah
* blah
* blah

The final day will be reserved to discussing next steps, particulary, what is required from the EDAM or bio.tools side, and identify concrete actions to finish off these works and write them up for publication. 



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
