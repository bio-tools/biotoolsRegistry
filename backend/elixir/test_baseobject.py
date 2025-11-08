import json
import os

from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch import exceptions as ESExceptions
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from elixir.views import Ontology, User

"""
IMPORTANT: When writing tests, set 'additionUpdate' and 'lastUpdate' to None! (or figure out a way to calculate the timestamps that the database will generate)
"""


class BaseTestObject(APITestCase):

    # initial setup of the test environment (loading the Ontology from file, etc)
    def setUp(self):
        """
        Method to prepare the testing environment; called before calling the test method.
        """

        # settings.ELASTIC_SEARCH_INDEX = 'test'
        self.maxDiff = None
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(
            "test_user", password="test_user_password", email="dupa@example.com"
        )
        self.user.save()
        token = Token.objects.create(user=self.user)
        token.save()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        self.client.login(username="test_user", password="test_user_password")

        es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)
        try:
            es.indices.delete(index=settings.ELASTIC_SEARCH_INDEX)
        except ESExceptions.TransportError as TE:
            if TE.status_code != 404:
                raise TE

        es.indices.create(settings.ELASTIC_SEARCH_INDEX)
        es.indices.put_mapping(index=settings.ELASTIC_SEARCH_INDEX, body=mapping)

        self.load_ontologies()

    def load_ontologies(self):
        path_data = "/elixir/application/backend/data"
        path_edam = path_data + "/edam/json/current"

        filenames = [
            "/EDAM_Topic.json",
            "/flat_EDAM_Topic.json",
            "/EDAM_Format.json",
            "/flat_EDAM_Format.json",
            "/EDAM_Data.json",
            "/flat_EDAM_Data.json",
            "/EDAM_Operation.json",
            "/flat_EDAM_Operation.json",
            "/EDAM_obsolete.json",
            "/flat_EDAM_obsolete.json",
        ]

        for filename in filenames:
            # fill database with ontologies
            with open(path_edam + filename) as f:
                o = json.load(f)
                Ontology.objects.create(name="EDAM_Topic", data=json.dumps(o))

    def tearDown(self):
        """
        Method called after the test method; only called if setup() succeeds, regardless of the test method outcome.
        """

        es = Elasticsearch(settings.ELASTIC_SEARCH_URLS)
        try:
            resp = es.indices.delete(index="test")
        except ESExceptions.TransportError as TE:
            if TE.status_code == 404:
                do_nothing = True
            else:
                raise TE
        settings.ELASTIC_SEARCH_INDEX = "elixir"
