from elasticsearch import Elasticsearch
from elixir import search
from elixir import stats
from elixir.serializers import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)

# From https://github.com/bio-tools/biotoolsSum/blob/master/public/config.js
# Column names are defined in home.html
# Queries follow the URL when searching on bio.tools, e.g., https://bio.tools/t?page=1&topic=DNA
DATA = [
    {
        "name": 'DNA',
        "cells": [
            {
                "route": 'dna-sequence-services',
                "image": 'dna-1d-services.png',
                "message": 'Services for DNA sequence analysis',
                "q": {"topic": "DNA", "operation": "Sequence analysis"}
            }, {
                "route": 'dna-structure-services',
                "image": 'dna-2d-services.png',
                "message": 'Services for DNA structure analysis and prediction',
                "q": {"topic": "DNA", "operation": "Structure prediction"}
            }, {
                "route": 'dna-function-services',
                "image": 'dna-3d-services.png',
                "message": 'Services for DNA function analysis',
                "q": {"topic": "DNA", "operation": "Genome annotation"}
            }, {
                "route": 'dna-quantification-services',
                "image": 'dna-xd-services.png',
                "message": 'Services for genomics and DNA quantification',
                "q": {"topic": "Genomics"}
            },
        ],
    },
    {
        "name": 'RNA',
        "cells": [
            {
                "route": 'rna-sequence-services',
                "image": 'rna-1d-services.png',
                "message": 'Services for RNA sequence analysis',
                "q": {"topic": "RNA", "operation": "Sequence analysis"}
            }, {
                "route": 'rna-structure-services',
                "image": 'rna-2d-services.png',
                "message": 'Services for RNA structure analysis and prediction',
                "q": {"topic": "RNA", "operation": "RNA structure prediction"}
            }, {
                "route": 'rna-function-services',
                "image": 'rna-3d-services.png',
                "message": 'Services for RNA function analysis',
                "q": {"topic": "RNA", "operation": "Gene prediction"}
            }, {
                "route": 'rna-quantification-services',
                "image": 'rna-xd-services.png',
                "message": 'Services for transcriptomics and RNA quantification',
                "q": {"topic": "Transcriptomics"}
            },
        ],
    },
    {
        "name": 'Protein',
        "cells": [
            {
                "route": 'protein-sequence-services',
                "image": 'protein-1d-services.png',
                "message": 'Services for protein sequence analysis',
                "q": {"topic": "Proteins", "operation": "Sequence analysis"}
            }, {
                "route": 'protein-structure-services',
                "image": 'protein-2d-services.png',
                "message": 'Services for protein structure analysis and prediction',
                "q": {"topic": "Protein structure", "operation": "Structure prediction"}
            }, {
                "route": 'protein-function-services',
                "image": 'protein-3d-services.png',
                "message": 'Services for protein function analysis',
                "q": {"topic": "Proteins", "operation": "Protein function prediction"}
            }, {
                "route": 'protein-quantification-services',
                "image": 'protein-xd-services.png',
                "message": 'Services for proteomics and protein quantification',
                "q": {"topic": "Proteomics"}
            },
        ],
    },
    {
        "name": 'Small molecules',
        "cells": [
            {
                "route": 'molecule-sequence-services',
                "image": 'drug-1d-services.png',
                "message": 'Services for small molecule structure representation',
                "q": {"topic": "Small molecules", "operation": "Format validation"}
            }, {
                "route": 'molecule-structure-services',
                "image": 'drug-2d-services.png',
                "message": 'Services for small molecule structure analysis',
                "q": {"topic": "Small molecules", "operation": "Molecular dynamics"}
            }, {
                "route": 'molecule-function-services',
                "image": 'drug-3d-services.png',
                "message": 'Services for small molecule function and interaction analysis',
                "q": {"topic": "Small molecules", "operation": "Protein-ligand docking"}
            }, {
                "route": 'molecule-quantification-services',
                "image": 'drug-xd-services.png',
                "message": 'Services for metabolomics and small molecule quantification',
                "q": {"topic": "Metabolomics"}
            },
        ],
    },
]


class ToolMatrix(APIView):
    """
    Get a matrix of tool classes
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None):
        query = request.GET

        # Get count of tools for a query
        def get_count(q: dict) -> int:
            query_struct = search.construct_es_query(q)
            result = es.search(index=settings.ELASTIC_SEARCH_INDEX, body=query_struct)
            count = result['hits']['total']['value']
            return count

        def fix_query(q: dict) -> dict:
            if isinstance(q, str):
                q = {"q": q}
            q = {k: f"'{v}'" for k, v in q.items()}
            return q

        response = DATA[:]

        # Put the queries into quotes so searching isn't fuzzy

        # Append a 'count' to every cell in the DATA matrix
        for row in response:
            for cell in row['cells']:
                query = fix_query(cell['q'])
                cell['count'] = get_count(query)

                # Also append a URL encoded query link
                if not isinstance(query, str):
                    cell["link"] = "&".join([f"{k}={v}" for k, v in query.items()])

        # Flatten the data to a format angularjs can use
        flat = []
        for row in response:
            flat.append({"name": row['name'], "head": True})
            for cell in row['cells']:
                x = cell
                x["head"] = False
                flat.append(x)

        # Append a 'total'
        statsInfo = stats.StatsInfo()
        response = {
            "data": flat,
            "total": statsInfo.totalEntries()
        }

        return Response(response)
