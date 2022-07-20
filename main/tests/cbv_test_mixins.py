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
        '''
            Tests unauthenticated access in case view has LoginRequired mixin.
        '''
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEquals(response.status_code, 302)

    def test_get(self):    
        '''
            Tests get request response has status 200 and 
            response context has expected keys.
        ''' 
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
        '''
            Test post request with valid data.
        '''
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
        '''
            Test post request with invalid data.
        '''
        for data in self.invalid_data:
            with self.subTest(data=data):
                self.subtest_post_failure

    def test_view_function(self):
        '''
            Tests url resolves to view function.
        '''
        if self.view_function:
            match = resolve(self.test_url)
            self.assertEquals(self.function.__name__, match.func.__name__)


class TestListViewMixin(object):

    @classmethod
    def setUpTestData(cls):
        cls.test_url = None
        cls.model = None
        cls.context_list = None
        cls.template_name = None
        cls.function = None # Add .as_view()
        cls.login_required = False
        cls.model_factory = None
        cls.object_list_name = None

    def setUp(self) -> None:
        self.user = self.get_user()
        self.view_function = resolve(self.test_url)
        if self.login_required:
            self.client.force_login(self.user)

    def get_user(self):
        user = UserFactory()
        return user

    def test_unauthenticated_access(self):
        '''
            Tests unauthenticated access in case view has LoginRequired mixin.
        '''
        if not self.login_required:
            pass
        self.client.logout()
        response = self.client.get(self.test_url)
        self.assertEquals(response.status_code, 302)

    def test_get(self):   
        '''
            Tests get request response has status 200 and 
            response context has expected keys.
        ''' 
        response = self.client.get(self.test_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        # test context
        for item in self.context_list:
            self.assertIn(item, response.context.keys())

    def test_view_function(self):
        '''
            Tests url resolves to view function.
        '''
        if self.view_function:
            match = resolve(self.test_url)
            self.assertEquals(self.function.__name__, match.func.__name__)

    def test_queryset(self):
        '''
            Tests if response context has the expected queryset.
        '''
        if self.model_factory:
            self.model_factory.create_batch(5)
            qs = self.model.objects.all()
            response = self.client.get(self.test_url)
            context_qs = response.context[self.object_list_name]
            self.assertQuerysetEqual(qs, context_qs, ordered=False)