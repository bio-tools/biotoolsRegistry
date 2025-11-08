import dateutil.parser
import requests
from django.utils import timezone

from elixir.models import *


############################################################################
# Publication Metadata
############################################################################
def extract_publication_data(response):
    title = ""
    abstract = ""
    journal = ""
    authors = []
    date = None
    citation = None

    doi = response.get("doi", None)
    pmid = response.get("pmid", None)
    pmcid = response.get("pmcid", None)

    try:
        journal = response["journalInfo"]["journal"]["title"]
    except:
        print("Warning: Publication journal not available for publication.")
    try:
        date = dateutil.parser.parse(response["journalInfo"]["printPublicationDate"])
    except:
        print("Warning: Publication date not available for publication.")
    try:
        title = response["title"]
    except:
        print("Warning: Title not available for publication.")
    try:
        abstract = response["abstractText"]
    except:
        print("Warning: Abstract not available for publication.")
    try:
        for author in response["authorList"]["author"]:
            authors.append(author["fullName"])
    except:
        print("Warning: Authors not available for publication.")
    try:
        citation = response["citedByCount"]
    except:
        print("Warning: Cited by count not available for publication.")
    return {
        "doi": doi,
        "pmid": pmid,
        "pmcid": pmcid,
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "date": date,
        "journal": journal,
        "citation": citation,
    }


def fetch_publication_data(id_type, identifier, result_type):
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={id_type}:{identifier}&format=json&resultType={result_type}"
    headers = {"Accept": "application/json"}
    request = requests.get(url, headers=headers)

    if request.status_code == 200:
        results = request.json().get("resultList", {}).get("result", [])
        result = results[0] if results else None
        return extract_publication_data(result) if result else None

    return None


def publication_metadata_needs_update(publication):
    if publication.metadata is not None:
        updated = publication.metadata.updated
        if updated:
            if (timezone.now() - updated).days < 30:
                return False
    return True


def save_publication_data(data, citation_count, publication):
    if publication.metadata is not None:
        metadata = publication.metadata
    else:
        metadata = PublicationMetadata()
        metadata.save()
    metadata.title = data["title"]
    metadata.abstract = data["abstract"]
    metadata.publication = publication
    metadata.citationCount = data["citation"]
    metadata.journal = data["journal"]
    metadata.date = data["date"]
    metadata.updated = timezone.now()
    metadata.authors.all().delete()
    publication.metadata = metadata
    for author in data["authors"]:
        pub_author = PublicationAuthor()
        pub_author.name = author
        pub_author.metadata = metadata
        pub_author.save()

    # update missing identifiers
    if not publication.doi and data["doi"]:
        publication.doi = data["doi"]
    if not publication.pmid and data["pmid"]:
        publication.pmid = data["pmid"]
    if not publication.pmcid and data["pmcid"]:
        publication.pmcid = data["pmcid"]

    publication.save()
    metadata.save()


def update_publication(publication):
    try:
        data = None

        if publication.doi:
            if publication_metadata_needs_update(publication):
                data = fetch_publication_data(
                    "DOI", publication.doi.replace("doi:", ""), "core"
                )
        elif publication.pmid:
            if publication_metadata_needs_update(publication):
                data = fetch_publication_data("EXT_ID", publication.pmid, "core")
        elif publication.pmcid:
            if publication_metadata_needs_update(publication):
                data = fetch_publication_data(
                    "PMC", publication.pmcid.replace("PMC", ""), "core"
                )
        if data:
            save_publication_data(data, publication)
    except Exception as e:
        print("Warning: Publication could not be processed.", e)
