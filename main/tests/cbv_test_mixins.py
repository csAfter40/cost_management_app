from django.db import models
from main.tests.factories import UserFactory
from django.urls import resolve


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
        cls.function = None # Add .as_view()

    def setUp(self) -> None:
        self.user = self.get_user()
        self.client.force_login(self.user)
        self.view_function = resolve(self.test_url)

    def get_user(self):
        user = UserFactory()
        return user

    def get_object(self):
        return self.model.objects.all().last()

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEquals(response.status_code, 302)

    def test_get(self):    
        response = self.client.get(self.test_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        # test context
        for item in self.context_list:
            self.assertIn(item, response.context.keys())

    def subtest_post_success(self, data):
        response = self.client.post(self.test_url, data=data)
        # test response code
        self.assertRedirects(response, self.success_url, status_code=302, target_status_code=200, fetch_redirect_response=True)
        # test created object
        self.valid_object = self.get_object()
        self.assertNotEquals(self.valid_object, None)
        for key, value in data.items():
            if isinstance(getattr(self.valid_object, key), models.Model):
                self.assertEquals(getattr(self.valid_object, key).id, value)
            else:
                self.assertEquals(getattr(self.valid_object, key), value)

    def test_post_success(self):
        for data in self.valid_data:
            with self.subTest(data=data):
                self.subtest_post_success(data)

    def subtest_post_failure(self, data):
        response = self.client.post(self.test_url, data=data)
        # test response code
        self.assertEquals(response.status_code, 200)
        # test no objects are created
        invalid_object = self.get_object()
        self.assertEquals(invalid_object, None)

    def test_post_failure(self):
        for data in self.invalid_data:
            with self.subTest(data=data):
                self.subtest_post_failure

    def test_view_function(self):
        if self.view_function:
            match = resolve(self.test_url)
            self.assertEquals(self.function.__name__, match.func.__name__)