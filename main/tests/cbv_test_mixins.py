from cgi import test
from django.db import models
from django.test import Client
from main.tests.factories import UserFactory


class TestCreateViewMixin(object):

    @classmethod
    def setUpTestData(cls):
        cls.test_url = None
        cls.success_url = None
        cls.model = None
        cls.context_list = None
        cls.template_name = None
        cls.valid_data = None
        cls.invalid_data = None

    def setUp(self) -> None:
        self.user = self.get_user()
        self.client = Client()

    def get_user(self):
        user = UserFactory()
        return user

    def get_object(self):
        return self.model.objects.all().last()

    def test_unauthenticated_access(self):
        response = self.client.get(self.test_url)
        assert response.status_code == 302

    def test_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.test_url)
        assert response.status_code == 200
        assert response.template_name[0] == self.template_name        
        # test context
        for item in self.context_list:
            assert item in response.context.keys()

    def subtest_post_success(self, data):
        self.client.force_login(self.user)
        response = self.client.post(self.test_url, data=data)
        # test response code
        assert response.status_code == 302
        # test created object
        self.valid_object = self.get_object()
        assert self.valid_object != None
        for key, value in data.items():
            if isinstance(getattr(self.valid_object, key), models.Model):
                assert getattr(self.valid_object, key).id == value
            else:
                assert getattr(self.valid_object, key) == value
        # test success redirect url
        assert self.success_url in response.get('Location')

    def test_post_success(self):
        for data in self.valid_data:
            with self.subTest(data=data):
                self.subtest_post_success(data)

    def subtest_post_failure(self, data):
        self.client.force_login(self.user)
        response = self.client.post(self.test_url, data=data)
        # test response code
        assert response.status_code == 200
        # test no objects are created
        invalid_object = self.get_object()
        assert invalid_object == None

    def test_post_failure(self):
        for data in self.invalid_data:
            with self.subTest(data=data):
                self.subtest_post_failure