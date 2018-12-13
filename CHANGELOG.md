# Changelog
All notable changes to *bio.tools* will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]


## Dec 14th 2018
### Added
- [(392)](https://github.com/bio-tools/biotoolsRegistry/issues/392) [Dimensions badge](https://badge.dimensions.ai/) added to Tool Cards to render **citation information** and link out to **research insights**.
- [(391)](https://github.com/bio-tools/biotoolsRegistry/issues/391) New ELIXIR-branded  **bio.tools** logo replacing vanilla ELIXIR logo.
- [(374)](https://github.com/bio-tools/biotoolsRegistry/issues/374) Added **tool operations** to compact / mini-card view
- [(327)](https://github.com/bio-tools/biotoolsRegistry/issues/327) **Interactive annnotations**: clicking on a label (topic, operation, data or format) now perform a search within *bio.tools*
	
	
### Changed
- greatly enriched API parameters allow **precise queries** over tool function and other metadata.  See [API reference](https://biotools.readthedocs.io/en/latest/api_reference_dev.html) and [API Usage Guide](https://biotools.readthedocs.io/en/latest/api_usage_guide_dev.html).
- [(385)](https://github.com/bio-tools/biotoolsRegistry/issues/385) **Enhanced faceting** in the search box allowing specific search with autocompletion for operation, tool type, language, accessibility, cost and license.
- [(383)](https://github.com/bio-tools/biotoolsRegistry/issues/383) **Tool tips** on function diagram explain to users the meaning of annotation and behaviour when clicked.
- [(374)](https://github.com/bio-tools/biotoolsRegistry/issues/374) Changed **colour of UI elements** to match the [EDAM colour scheme](https://github.com/edamontology/edamontology/issues/340)

### Deprecated

### Removed
- [(379)](https://github.com/bio-tools/biotoolsRegistry/issues/379) Removed (now uneccessary) rendering of "None" for version information.
- [(375)](https://github.com/bio-tools/biotoolsRegistry/issues/375) Replaced webpage at https://bio.tools/schema with redirect to [biotoolsSchema repo](http://github.com/bio-tools/biotoolsschema)

### Fixed
- [(386)](https://github.com/bio-tools/biotoolsRegistry/issues/386) Fixed 160 **tool descriptions** that were invalid according to [biotoolsSchema 3.0.0](https://github.com/bio-tools/biotoolsSchema/tree/master/versions/biotools-3.0.0).
- [(384)](https://github.com/bio-tools/biotoolsRegistry/issues/384) Fixed overly long **collection IDs** that were invalid according to [biotoolsSchema 3.0.0](https://github.com/bio-tools/biotoolsSchema/tree/master/versions/biotools-3.0.0).
- [(343)](https://github.com/bio-tools/biotoolsRegistry/issues/343) Fixed bug in search for formats.
- [(337)](https://github.com/bio-tools/biotoolsRegistry/issues/337) Fixed invalid DOIs and DOI validation.	
- [(371)](https://github.com/bio-tools/biotoolsRegistry/issues/371), [(367)](https://github.com/bio-tools/biotoolsRegistry/issues/367) Misc. **content clean-ups**

### Security
- [()]()




