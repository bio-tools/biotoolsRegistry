# bio.tools & EDAM drop-in hackathon & discussions

### Representative: Jon Ison

*DETAILS BELOW ARE PROVISIONAL AND MAY CHANGE IN THE RUN-UP TO THE EVENT*

## Community

[ELIXIR Tools Platform](https://www.elixir-europe.org/platforms/tools), [bio.tools](https://github.com/bio-tools/biotoolsregistry/), [EDAM](https://github.com/edamontology/edamontology/)

## Leads
* Jon Ison
* Hans-Ioan Ienasescu
* Matúš Kalaš 
* Hervé Ménager 
* Veit Schwämmle 


## Background information
EDAM and bio.tools developers will attend the whole hackathon (Mon 12 - Fri 16) and run dicussion and hacking sessions, with each day focused on a specific theme (see below).  We hope to work with any people and projects who are interested in using or developing EDAM and bio.tools.

## Focus of each day
Each hackathon day has a focus, which we'll try to stick to, with a range of tasks catering for different interests and expertise.  We do not expect to complete all the tasks, and will adapt depending upon who turns up, so feel free to drop in to any session at any time:

* **Tue Nov 13** [bio.tools testing](https://github.com/bio-tools/biotoolsRegistry/blob/master/biohackathon.md#day-2-nov-13-biotools-testing) (testing & search optimisation)
* **Tue Nov 14** [bio.tools outreach](https://github.com/bio-tools/biotoolsRegistry/blob/master/biohackathon.md#day-3-nov-14-biotools-outreach) (kick-start the community development)
* **Wed Nov 15** [EDAM development](https://github.com/bio-tools/biotoolsRegistry/blob/master/biohackathon.md#day-4-nov-15-edam-development) (data formats catalogue, planning EDAM 2.0 and applications)
* **Fri Nov 16** [Planning](https://github.com/bio-tools/biotoolsRegistry/blob/master/biohackathon.md#day-5-nov-16-planning--coordination) (wrapping up, next steps, collaborations)


---
## Day 1 (Nov 12): Warm-up
*EDAM and bio.tools core-dev will be around to discuss sessions for days 2-5*


---
## Day 2 (Nov 13): bio.tools testing
**Expected audience:** *anyone with an interest in improving bio.tools*

**Expected outcome:** *verify the next release, improve the search performance*

The purpose is to test, evaluate and optimise the development deployment of bio.tools (https://dev.bio.tools/), changes in which are scheduled to be moved into production (https://bio.tools/) during Dec 3-7.  The bio.tools core-dev will be on hand to discuss things in person.

### Task 1: Release testing
Currently 28 issues labelled ["done - staged for release"](https://github.com/bio-tools/biotoolsregistry/issues?q=is%3Aissue+is%3Aopen+label%3A%22done+-+staged+for+release%22) are implemented in https://dev.bio.tools.  Before these can be moved into production, we need independent verification that these features and fixes are satisfactorily implemented.

The task is:
* pick any ["done - staged for release"](https://github.com/bio-tools/biotoolsregistry/issues?q=is%3Aissue+is%3Aopen+label%3A%22done+-+staged+for+release%22) issue which lacks the ["fix verified"](https://github.com/bio-tools/biotoolsRegistry/labels/fix%20verified) label
* read the thread and test things are working as advertised
* add a comment to the thread; either reporting things are OK, or describing an outstanding problem: bio.tools core-dev will monitor the tracker, fix issues that crop up, and attach the ```fix verified``` label to confirmed fixes
* repeat, until all ```done - staged for release``` issues are verified

Alternatively:
* experiment with https://dev.bio.tools - critique the interfaces, API and content - and report any bugs or suggestions via [GitHub](https://github.com/bio-tools/biotoolsRegistry/issues/new)

### Task 2: bio.tools API testing & optimisation
The latest development deployment of the bio.tools API (https://dev.bio.tools/api/tool) is, we hope, a big improvement on the current version.  It supports a comprehensive [set of parameters](https://biotools.readthedocs.io/en/latest/api_reference_dev.html) that enable precise query over tool function and other metadata.  But before we can move these changes into production, the API needs to be thoroughly tested.  We also want to optimise the search behaviour, in light of results of real user experiments, to ensure it works as anticipated.

The task is:
* systematically test the API, particulaly the behaviour of the search parameters as documented in the [API Reference](https://biotools.readthedocs.io/en/latest/api_reference_dev.html) and [API Usage Guide](https://biotools.readthedocs.io/en/latest/api_usage_guide_dev.html).
* provide feedback on the API search behaviour / possible improvement via [GitHub](https://github.com/bio-tools/biotoolsRegistry/issues/new).  You can suggest fixes or improvements to the API docs [here](https://github.com/bio-tools/biotoolsdocs/issues).
* *elasticsearch experts only* - please speak to bio.tools core-dev (there are issues we need help with!)

We hope (developments pending) to have an easy way to tweak the elasticsearch parameters during the workshop, allowing for immediate iterative improvements.

---
## Day 3 (Nov 14): bio.tools outreach
**Expected audience:** *anyone with an interest in developing bio.tools*

**Expected outcome:** *kick-start the community development process*

The purpose is introduce our current development priorities and to introduce and improve the proposed community development process for bio.tools. The bio.tools core-dev will be on hand to discuss things in person.

### Task 1: Development priorities
We label issues to reflect their status and priority:
* ["critical priority"](https://github.com/bio-tools/biotoolsRegistry/labels/critical%20priority) : our top priorities, including most of the reported [bugs](https://github.com/bio-tools/biotoolsRegistry/labels/bug)
* ["high priority"](https://github.com/bio-tools/biotoolsRegistry/issues?q=is%3Aissue+is%3Aopen+label%3A%22high+priority%22) : things which bio.tools core-dev consider high priorities; we get to these once ["critical priority"](https://github.com/bio-tools/biotoolsRegistry/labels/critical%20priority) issues are addressed
* ["in progress"](https://github.com/bio-tools/biotoolsRegistry/labels/in%20progress) : things we're working on currently
* ["Dec 18 release"](https://github.com/bio-tools/biotoolsRegistry/milestone/2) : things we're aiming to put into the next production deployment
* ["wontfixsoon"](https://github.com/bio-tools/biotoolsRegistry/labels/wontfixsoon) : things which, for one reason or another (usually lack of developer capacity), we don't anticipate doing soon (that's doesn't imply they're unimportant or bad ideas!)

We want to be sure our priorities reflect those of the community at large, and engage developers who are willing to help out.  The task is:
* review our priorities (issues in any of the categories above) - providing feedback in the appropriate GitHub thread
* feel free to [request new features](https://github.com/bio-tools/biotoolsRegistry/issues/new), but please first [search our issues](https://github.com/bio-tools/biotoolsRegistry/issues) as it might already be listed
* *developers only* - if you're interested to help out - especially on ["critical priority"](https://github.com/bio-tools/biotoolsRegistry/labels/critical%20priority) issues (or anything else!), then please disucss this with the bio.tools core-dev


### Task 2: Open development process
Now that bio.tools is [open source](https://github.com/bio-tools/biotoolsRegistry/blob/master/LICENSE), there is an opportunity for hackers everywhere to contribute to the project.  But first we must define how the community development process will work in practice.  We have emerging [contributor guidelines](https://github.com/bio-tools/biotoolsRegistry/blob/master/contribution.md) but we want to revise these in light of feedback from potential contributors.

The task is to review the emerging [contributor guidelines](https://github.com/bio-tools/biotoolsRegistry/blob/master/contribution.md), provide feedback on these via [GitHub](https://github.com/bio-tools/biotoolsRegistry/issues/new), or provide feedback in person to bio.tools core-dev.


---
## Day 4 (Nov 15): EDAM development
**Expected audience:** *anyone with an interest in improving EDAM, people knowledgeable of bioinformatics data formats*

**Expected outcome:** *improved EDAM Formats subontology, scoping the desired state of EDAM 2.0, developing EDAM applications*

### Task 1 Curation of bioinformatics data formats
The [EDAM Format subontology](http://edamontology.org/format_1915) has potential in systems such as [Galaxy](https://f1000research.com/posters/6-1032) and for applications such as [workflow composition](https://doi.org/10.1093/bioinformatics/bty646).  EDAM is close to providing a comprehensive catalogue of the prevalent bioinformatics data formats, but a significant amount of work remains.  The task is to work on any aspects of the data format curation listed [here](https://github.com/edamontology/edamontology/issues/370) including:

* addition of miscellaneous new data formats, or changes to existing ones (see [issues](https://github.com/edamontology/edamontology/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3A%22concept%2Fterm+request%22+format))
* addition of formats ensuring coverage for Galaxy applications ([issue](https://github.com/edamontology/edamontology/issues/85))
* addition of formats to ensure coverage of [FAIRSharing](https://fairsharing.org/)

We expect the tasks to be accomplished manually, programmatically, or by a combination of the two.  Please see:
* [guidelines](https://edamontologydocs.readthedocs.io/en/latest/editors_guide.html#id12) for EDAM Format curation
* [EDAM Format request template](https://github.com/edamontology/edamontology/issues/new/choose) (see the [docs](https://github.com/edamontology/edamontology/blob/master/.github/ISSUE_TEMPLATE/new-format.md))


### Task 2 Verification of EDAM Formats subontology
We have guidelines for the development of the EDAM formats subontology:
* [editor guidelines](https://edamontologydocs.readthedocs.io/en/latest/editors_guide.html#id12) when modifying EDAM; adding or changing concepts, concept metadata, crosslinking, etc.
* [developer guidelines](https://edamontologydocs.readthedocs.io/en/latest/developers_guide.html#adding-concepts) about the technical process

To develop EDAM Format subontology into a rigorous catalogue, we must ensure the guidelines are followed.  The task is:
* review the [editor guidelines](https://edamontologydocs.readthedocs.io/en/latest/editors_guide.html#id12) and [developer guidelines](https://edamontologydocs.readthedocs.io/en/latest/developers_guide.html#adding-concepts), and provide feedback on these via [GitHub](https://github.com/edamontology/edamontologyDocs/issues/new) or discuss this in person with EDAM core-dev
* propose clean-ups of the connection between EDAM Format and Data subontologies (see [issue](https://github.com/edamontology/edamontology/issues/283)) : please make suggestions via [GitHub](https://github.com/edamontology/edamontology/issues/new) - see also [issue](https://github.com/edamontology/edamontology/issues/287)
* (*developers only*) develop a utility that checks compliance of EDAM to the guidelines above, and generate a human-readable report that can be acted on.  In case you want to work with EDAM in JSON / JSON-LD format, see [edam2json](https://github.com/edamontology/edam2json)
  

### Task 3 Towards EDAM 2.0 (discussion & planning)
It's over 5 years since an [article](https://doi.org/10.1093/bioinformatics/btt113) describing EDAM was published in Bioinformatics.  Since then, there have been 18 new releases (currently EDAM 1.21), with many additions and improvements, and greatly improved documentation:
* rules for [concepts](https://edamontologydocs.readthedocs.io/en/latest/technical_details.html#concepts),
* rules for [hierarchy depth](https://edamontologydocs.readthedocs.io/en/latest/technical_details.html#hierarchy-depth)
* [guidelines for editors](https://edamontologydocs.readthedocs.io/en/latest/editors_guide.html)
* [guidelines for developers](https://edamontologydocs.readthedocs.io/en/latest/developers_guide.html)

Within 3 - 6 months, we hope to release EDAM 2.0 implementing a set of features representing a step forward in value and quality over the 1.* releases.  The task (working as a group, or alone) is:
* think; what are the desirable properties of EDAM 2.0?  Is it simply to adhere to the rules and guidelines above, or something more?
* enumerate desirable properties in this [issue](https://github.com/edamontology/edamontology/issues/376); we'll try to prioritise these during the hackathon
* create sub-issues as needed, for finer-grained information


### Task 4: EDAM applications (discussion & hacking)
EDAM is used (or being considered) in a variety of contexts.  There is an opportunity for developers on projects that are using (or considering) EDAM to discuss their requirements and work with the EDAM developers.  Or you might have an idea that we haven't heard of already; let's discuss.

---
## Day 5 (Nov 16): Planning & coordination

The final day will be reserved to finishing off, and discussing and planning next steps around collaborations of EDAM and bio.tools with other projects.

---
## More ...
We can work on other topics, depending upon interest and progress as we proceed, *e.g.*:

* workflows in bio.tools: modelling, visualisation and curation
* evaluation of [EDAM Browser](https://ifb-elixirfr.github.io/edam-browser/) (see [GitHub](https://github.com/IFB-ElixirFr/edam-browser)) ontology browser; issues, features and next steps
* bio.tools content from an end-user perspective: annotation consistency, EDAM coverage, content views *etc*
* integration of bio.tools and biocontainers.pro
* integration of bio.tools and Galaxy

If you're particularly interested in a topic, mail [Jon Ison](mailto:jison@bioinformatics@dtu.dk)



---
## Links & references
- https://bio.tools/
- https://bio-tools.github.io/Tool-Information-Standard/
- https://www.ebi.ac.uk/ols/ontologies/edam
- https://bioportal.bioontology.org/ontologies/EDAM
- https://ifb-elixirfr.github.io/edam-browser/

## GitHub repos
- https://github.com/bio-tools/biotoolsregistry
- https://github.com/bio-tools/biotoolsschema
- https://github.com/edamontology/edamontology/
- https://github.com/bio-tools/Tool-Information-Standard
- https://github.com/IFB-ElixirFr/edam-browser

## Docs
- https://biotools.readthedocs.io/en/latest/
- https://biotoolsschema.readthedocs.io/en/latest/
- https://edamontologydocs.readthedocs.io/en/latest/
