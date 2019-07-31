**CAUTION:: WORK IN PROGRESS - THINGS MAY CHANGE**


# Code repo / branch structure
The repo structure follows [branching standards & conventions](https://gist.github.com/digitaljhelms/4287848).  There are two main (permanent) branches ("dev" and "stable"), with other supporting (temporary) branches ("features-<id>", "bugfixes-<id>" and "hotfixes-<id>") each with a specific purpose.  Strict rules mandate which branches may be originating branches and which branches must be merge targets.


Instance     | Branch         | Comment
-----------  | ------         | -------
"stable"     | stable         | Accepts merges from "dev" and "hotfixes"
"dev"        | master         | Accepts merges from "features", "bugfixes" and "hotfixes"
"features"   | feature-\<id\> | Always branch off HEAD of "dev"
"bugfixes"   | bugfix-\<id\>  | Always branch off HEAD of "dev"
"hotfixes"   | hotfix-\<id\>  | Always branch off "stable"


- **"dev" branch** (`origin/master`) (code deployed on https://dev.bio.tools) 
  - the default / base branch of the repo, against which all pull requests and code pushes are automatically made
  - holds changes for the next release
  - developers will branch from / merge to it
  - accepts pull requests (see [Community Development Guidelines](https://github.com/bio-tools/biotoolsRegistry/blob/master/contribution.md#community-development-guidelines))

- **"stable"** branch (`origin/stable`) (code deployed on https://bio.tools) 
  - latest code deployed to (and allowing bug fixing of) production system
  - not normally interacted with (other than hot fixes)
  - periodically updated from "dev" branch (see [Release Process](https://github.com/bio-tools/biotoolsRegistry/blob/master/contribution.md#release-process)
- **"feature"** and **"bug"** branches
  - **"feature"** branches are created for significant new features / enhancements (*i.e.* whose development may take longer than a single deployment) 
  - **"bug"** branches are created to address - in the next deployment - bugs found on the live site (a bug branch typically lasts one deployment cycle only)
  - should always be publicly available (development should never exist in just one developer's local branch)
  - always branch from, and merge back into "dev" branch
  - feature developer (or bug fixer) must watch the "dev" branch for pushes, ensuring all changes to it are merged into the feature/bug fix before merging back to "dev" (ideally as one goes along, to make conflict resolution easier)
  - branch naming convention, where `<id>` is a GitHub issue number (all features and bugs should be tracked as GitHub issues):

    - `feature-<id>`
    - `bug-<id>`

- **"hotfix"** branches
  - created when there's a need to immediately fix a problem with the production system (changes can be pushed any time, outside of scheduled deployment)
  - always branch from "stable" (and tag the branch), and merge back into both "stable" and "dev"

    - development of "dev" can continue while the hotfix is being addressed
    - tagged stable branch still represents what is in production.
    
  - branch naming convention:

    - `hotfix-<id>`

# Governance, roles & responsibilities
The Danish ELIXIR node provides stable funding for bio.tools as part of the ELIXIR-DK Service Delivery Plan.  bio.tools strives to be a "do-ocracy", *i.e.* driven primarily on a day-to-day basis by the people most active in developing the software and content, whilst respecting the executive / decision-making power of ELIXIR-DK management.  We follow a simple governance model:

- **bio.tools core-dev**

  - people with significant capacity (*e.g.* funded) to develop bio.tools 
  - can push changes to "dev" branch

- **bio.tools dev**

  - people with some capacity develop bio.tools (whether funded or not)
  - can make pull requests on "dev" and "stable" branches

- **Release Manager** (currently [Hans Ienasescu](mailto:hans@bio.tools) and [Piotr Chmura](mailto:piotr.chmura@cpr.ku.dk))

  - can push changes to "stable" branch (merging from "dev" or "hotfixes")
  - responsible for:

    - building the "stable" (https://bio.tools) and "dev" (https://dev.bio.tools) deployments, as per the [release process](https://github.com/bio-tools/biotoolsRegistry/blob/master/contribution.md#release-process)
    - ensuring all changes to "dev" deployment are thoroughly (and independently) tested before being pushed to production

- **Community Leader** (currently [Jon Ison](mailto:jison@bioinformatics.dtu.dk)) responsibilities:

  - ensure significant proposed changes are discussed, seeking consensus amongst core-dev (at least) ahead of implementation
  - settle with core-dev what features and fixes will go into the next milestone (and when)
  - settle disputes and decide (in case of disagreements) what is pushed to "stable" branch
  - announce changes to "dev" deployment, allowing adequate time for testing and evaluation
  - announce planned and actual changes to "stable" deployment (esp. any potentially breaking changes to API) via all available channels
  - maintain the issue tracker, creating, [labelling](https://github.com/bio-tools/biotoolsRegistry/blob/master/contribution.md#issue-tracking--labelling) and closing issues as required
    - manage the "core-dev" and "dev" groups (repo permissions, mailing lists, *etc.*)
  - oversee (and promote where necessary) the [code of conduct](https://github.com/bio-tools/biotoolsRegistry/blob/master/contribution.md#community-code-of-conduct) 

*All developers* must:

  - ensure proposed new features or other change are logged in the [issue tracker](https://github.com/bio-tools/biotoolsregistry/issues) and discussed, before coding
  - follow the [code of conduct](https://github.com/bio-tools/biotoolsRegistry/blob/master/contribution.md#community-code-of-conduct)  


# Issue tracking & labelling
Issues are [labelled](https://github.com/bio-tools/biotoolsregistry/labels), the most important labels being:
- ["critical priority"](https://github.com/bio-tools/biotoolsRegistry/labels/critical%20priority) : Our top priorities, including most of the reported bugs.
- ["high priority"](https://github.com/bio-tools/biotoolsRegistry/labels/high%20priority) : We get to these once "critical priority" issues are done.
- ["in progress"](https://github.com/bio-tools/biotoolsRegistry/labels/in%20progress) : Stuff we're actively working on.
- ["done - staged for release"](https://github.com/bio-tools/biotoolsRegistry/labels/done%20-%20staged%20for%20release) : Issue is implemented in dev.bio.tools.
- ["fix verified"](https://github.com/bio-tools/biotoolsRegistry/labels/fix%20verified) : fix verified An issue labelled "done - staged for release" has been independently verified as working OK.


# Release process
*tbd*, see https://github.com/bio-tools/biotoolsRegistry/issues/369


# Community development guidelines 
*tbd*, see https://github.com/bio-tools/biotoolsRegistry/issues/369



# Community code of conduct

This code of conduct outlines our expectations for the bio.tools developer community.  It is based loosely on the [GCCBOSC 2018 Code of Conduct](https://galaxyproject.org/events/gccbosc2018/code-of-conduct/#gccbosc-2018-code-of-conduct).  We are committed to providing a welcoming and productive community for all and expect our code of conduct to be honored.  Our open source community strives to be:

- **Considerate:** You depend upon the work of others who in turn depend on you.  You're unlikely to be fully aware of the ramifications of your proposals or actions, and the constraints others work under.  Before deciding or acting, talk to others and reach a common understanding of the consequences. 
- **Constructive:** We will not agree all the time.  Where we disagree, try to understand why and maintain a positive attitude in seeking a resolution, bearing in mind we share a common goal.
- **Supportive:**  Support others in their work (you depend on them!), respecting the fact that we have different levels of experience and technical ability.
- **Open-minded:** We have a wide range of backgrounds, skills and perspectives -  this diversity is a strength.  Be wary of ignoring or misunderstanding another viewpoint in the vindication of your own.
- **Respectful:** Disagreement and differences do not excuse bad manners. Never allow frustration to turn into aggressive conduct or a personal attack.  A happy atmosphere is a productive one:  be nice, and keep a sense of humour.  If you can't be nice, be quiet.
- **Tolerant:**  Treat people fairly and equally irrespective of their background and identity, including technical ability, experience, education, race, gender, nationality, age *etc*.
- **Wise:** We are not infallible; we will make mistakes and change our viewpoints: admit and learn from mistakes and allow others to do the same.  

## Conflict resolution
If you are unhappy in regard to the code of conduct not being honoured, you should raise your concerns immediately and try to resolve them, either directly with the person concerned, or failing that with the nominated *community leader* (currently [Jon Ison](mailto:jison@bioinformatics.dtu.dk)) who will try to resolve the issue discretely and fairly. 
