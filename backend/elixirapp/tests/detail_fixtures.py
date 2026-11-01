"""Fictional, local-only record shared by detail tests and the prototype seed."""
from datetime import datetime, timezone

from django.db import transaction

from elixir.models import (
    Resource, EditPermission, Version, ToolType, Language, OperatingSystem, Topic,
    Function, Operation, Input, Output, Data, Format, Publication, PublicationMetadata,
    PublicationAuthor, PublicationType, Credit, CreditTypeRole, Documentation,
    DocumentationType, Download, Link, LinkType, Relation, OtherID, CollectionID,
    ElixirCommunity, ElixirNode, ElixirPlatform,
)


@transaction.atomic
def create_detail_fixture(owner, identifier='detail-demo'):
    tool = Resource.objects.create(
        biotoolsID=identifier, biotoolsCURIE='biotools:' + identifier,
        name='Sequence Workbench (demo)', homepage='https://example.org/sequence-workbench',
        description='A local demonstration record for a sequence analysis workbench. '
                    'It brings together sequence alignment, format conversion and annotated results.\n\n'
                    'This fictional record contains representative bio.tools metadata; '
                    'its software, contributors and publication are illustrative.',
        owner=owner, editPermission=EditPermission.objects.create(type='private'),
        license='MIT', maturity='Mature', cost='Free of charge', accessibility='Open access',
        additionDate=datetime(2025, 4, 16, tzinfo=timezone.utc), confidence_flag='tool')
    Version.objects.create(resource=tool, version='2.4.0')
    Version.objects.create(resource=tool, version='2.3.1')
    ToolType.objects.create(resource=tool, name='Command-line tool')
    ToolType.objects.create(resource=tool, name='Web application')
    Language.objects.create(resource=tool, name='Python')
    OperatingSystem.objects.create(resource=tool, name='Linux')
    OperatingSystem.objects.create(resource=tool, name='Mac')
    Topic.objects.create(resource=tool, term='Sequence analysis', uri='http://edamontology.org/topic_0080')
    function = Function.objects.create(resource=tool, note='Align multiple sequences before downstream analysis.',
                                       cmd='sequence-workbench align --input sequences.fasta')
    Operation.objects.create(function=function, term='Sequence alignment', uri='http://edamontology.org/operation_2928')
    input_data = Input.objects.create(function=function, data=Data.objects.create(
        term='Sequence', uri='http://edamontology.org/data_2044'))
    Format.objects.create(input=input_data, term='FASTA', uri='http://edamontology.org/format_1929')
    output_data = Output.objects.create(function=function, data=Data.objects.create(
        term='Sequence alignment', uri='http://edamontology.org/data_0863'))
    Format.objects.create(output=output_data, term='ClustalW', uri='http://edamontology.org/format_1982')
    metadata = PublicationMetadata.objects.create(
        title='Sequence Workbench: a demonstration publication', journal='Example Methods',
        date=datetime(2025, 3, 1, tzinfo=timezone.utc), updated=datetime.now(timezone.utc),
        abstract='Illustrative abstract for the local prototype. No scientific publication is claimed.')
    PublicationAuthor.objects.create(metadata=metadata, name='Example Research Team')
    # Explicit fixture metadata must not trigger the publication-enrichment network signal.
    publication = Publication(resource=tool, doi='10.5555/detail-demo', metadata=metadata,
                              note='Fictional citation for interface testing.')
    Publication.objects.bulk_create([publication])
    publication = Publication.objects.get(metadata=metadata)
    PublicationType.objects.create(publication=publication, type='Primary')
    credit = Credit.objects.create(resource=tool, name='Example Research Team', typeEntity='Consortium',
                                   url='https://example.org/team', email='team@example.org',
                                   note='Maintains the demonstration record.')
    CreditTypeRole.objects.create(credit=credit, typeRole='Developer')
    CreditTypeRole.objects.create(credit=credit, typeRole='Maintainer')
    documentation = Documentation.objects.create(resource=tool, url='https://example.org/sequence-workbench/docs',
                                                note='Installation, command reference and worked examples.')
    DocumentationType.objects.create(documentation=documentation, type='User manual')
    Download.objects.create(resource=tool, type='Source code', version='2.4.0',
                            url='https://example.org/sequence-workbench/source',
                            cmd='pip install sequence-workbench-demo', note='Illustrative download only.')
    link = Link.objects.create(resource=tool, url='https://example.org/sequence-workbench/issues',
                               note='Example issue tracker.')
    LinkType.objects.create(link=link, type='Issue tracker')
    Relation.objects.create(resource=tool, biotoolsID='migration-fixture', type='isRelatedTo')
    OtherID.objects.create(resource=tool, type='doi', value='10.5555/detail-demo-software', version='2.4.0')
    CollectionID.objects.create(resource=tool, name='Local demonstration')
    ElixirCommunity.objects.create(resource=tool, elixirCommunity='Proteomics')
    ElixirNode.objects.create(resource=tool, elixirNode='Denmark')
    ElixirPlatform.objects.create(resource=tool, elixirPlatform='Tools')
    return tool
