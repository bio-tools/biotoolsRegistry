from elixir.models import *
from django.utils import timezone
import dateutil.parser
import requests
import json

############################################################################
# Publication Metadata
############################################################################
def extract_publication_data(response):
    title = ''
    abstract = ''
    journal = ''
    authors = []
    date = None
    try:
        journal = response['abstracts-retrieval-response']['coredata']['prism:publicationName']
    except:
        print("Warning: Publication journal not avaliable for publication.")
    try:
        date = dateutil.parser.parse(response['abstracts-retrieval-response']['coredata']['prism:coverDate'])
    except:
        print("Warning: Publication date not avaliable for publication.")
    print()
    try:
        title = response['abstracts-retrieval-response']['coredata']['dc:title']
    except:
        print("Warning: Title not avaliable for publication.")
    try:
        abstract = response['abstracts-retrieval-response']['coredata']['dc:description']
    except:
        print("Warning: Abstract not avaliable for publication.")
    try:
        for author in response['abstracts-retrieval-response']['authors']['author']:
            authors.append(author['ce:indexed-name'])
    except:
        print("Warning: Authors not avaliable for publication.")
    return {"title": title, "abstract": abstract, "authors": authors, "date": date, "journal": journal}

def extract_publication_citation(response):
    citation = None
    try:
        citation = response['search-results']['entry'][0]['citedby-count']
    except:
        print("Warning: Citations not avaliable for publication.")
    return citation
    
def fetch_publication_data(identifier):
    url = 'http://api.elsevier.com/content/abstract/' + identifier
    headers = {'Accept': 'application/json', 'X-ELS-APIKey': 'ddd4165bfdfe4dc9d3fb4b289aa321fe'}
    request = requests.get(url, headers=headers)
    if request.status_code == 200:
        return extract_publication_data(request.json())
    #print("failed")
    return None

def fetch_publication_citation(identifier):
    url = 'http://api.elsevier.com/content/search/scopus'
    headers = {'Accept': 'application/json', 'X-ELS-APIKey': 'ddd4165bfdfe4dc9d3fb4b289aa321fe'}
    params = {'query': identifier, 'field': 'citedby-count'}
    request = requests.get(url, params=params, headers=headers)
    if request.status_code == 200:
        return extract_publication_citation(request.json())
    #print("failed")
    return None

def publication_metadata_needs_update(publication):
    if publication.metadata != None:
        updated = publication.metadata.updated
        if updated:
            if (timezone.now() - updated).days < 30:
                #print("Updated: " + str((timezone.now() - updated).days) + " days ago. No need to update")
                return False
            #else:
                #print("Updated: " + str((timezone.now() - updated).days) + " days ago. Updating...")
    return True

def save_publication_data(data, citation_count, publication):
    if publication.metadata != None:
        metadata = publication.metadata
    else:
        metadata = PublicationMetadata()
        metadata.save()
    metadata.title = data['title']
    metadata.abstract = data['abstract']
    metadata.publication = publication
    metadata.citationCount = citation_count
    metadata.journal = data['journal']
    metadata.date = data['date']
    metadata.updated = timezone.now()
    metadata.authors.all().delete()
    publication.metadata = metadata
    for author in data['authors']:
        pub_author = PublicationAuthor()
        pub_author.name = author
        pub_author.metadata = metadata
        pub_author.save()
    publication.save()
    metadata.save()
    #print("saved")

def update_publication(publication):
    try:
        data = None
        
        if publication.doi:
            #print("Fetching metadata for: " + 'doi/' + publication.doi.replace('doi:',''))
            if publication_metadata_needs_update(publication):
                count = fetch_publication_citation('doi(' + publication.doi.replace('doi:','') + ')')
                data = fetch_publication_data('doi/' + publication.doi.replace('doi:',''))
        elif publication.pmid:
            #print("Fetching metadata for: " + 'pubmed_id/' + publication.pmid)
            if publication_metadata_needs_update(publication):
                count = fetch_publication_citation('pmid(' + publication.pmid + ')')
                data = fetch_publication_data('pubmed_id/' + publication.pmid)
        elif publication.pmcid:
            #print("Fetching metadata for: " + 'pubmed_id/' + publication.pmcid)
            if publication_metadata_needs_update(publication):
                count = fetch_publication_citation('pmid(' + publication.pmcid + ')')
                data = fetch_publication_data('pubmed_id/' + publication.pmcid)
        if data != None: 
            save_publication_data(data, count, publication)
    except:
        print("Warning: Publication could not be processed.")
        