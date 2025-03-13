from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from rest_framework.authtoken.models import Token
from elixir.views import Ontology, User

class BaseTestObject(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_superuser('test_superuser', password='test_superuser_password', email='test@superuser.com')
        self.user.save()
        token = Token.objects.create(user=self.user)
        token.save()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.client.login(username='test_superuser', password='test_superuser_password')
