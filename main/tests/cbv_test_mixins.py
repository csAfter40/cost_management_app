from django.db import models
from main.tests.factories import UserFactory
from django.urls import resolve
from django.core.exceptions import ImproperlyConfigured
import logging


class TestCreateViewMixin(object):

    @classmethod
    def setUpTestData(cls):
        cls.test_url = None
        cls.success_url = None
        cls.model = None
        cls.context_list = None
        cls.template = None
        cls.valid_data = None
        cls.invalid_data = None
        cls.view_function = None # Add .as_view()
        cls.login_required = False

    def setUp(self) -> None:
        self.user = self.get_user()
        if not self.test_url:
            raise ImproperlyConfigured('No test url available. Please provide a test_url')
        if self.login_required:
            self.client.force_login(self.user)

    def get_user(self):
        user = UserFactory()
        return user

    def get_object(self):
        if not self.model:
            raise ImproperlyConfigured('No model available. Please provide a model.')
        return self.model.objects.all().last()

    def test_unauthenticated_access(self):
        '''
            Tests unauthenticated access in case view has LoginRequired mixin.
        '''
        if not self.login_required:
            return
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
        # test template
        if self.template:
            self.assertTemplateUsed(response, self.template)
        else:
            logging.warning('\nWarning: No template available. Template test not implemented.')
        # test context
        if self.context_list:
            for item in self.context_list:
                self.assertIn(item, response.context.keys())
        else:
            logging.warning('\nWarning: No context_list available. Context test not implemented.')

    def subtest_post_success(self, data):
        response = self.client.post(self.test_url, data=data)
        # test response code
        if not self.success_url:
            raise ImproperlyConfigured('No URL to redirect to. Please provide a success_url.')
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
        if not self.view_function:
            raise ImproperlyConfigured('No view function available. Please provide a view_function.')
        match = resolve(self.test_url)
        self.assertEquals(self.view_function.__name__, match.func.__name__)


class TestListViewMixin(object):

    @classmethod
    def setUpTestData(cls):
        cls.test_url = None
        cls.model = None
        cls.context_list = None
        cls.template = None
        cls.view_function = None # Add .as_view()
        cls.login_required = False
        cls.model_factory = None
        cls.object_list_name = 'object_list'

    def setUp(self) -> None:
        self.user = self.get_user()
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
            return
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
        # test template
        if self.template:
            self.assertTemplateUsed(response, self.template)
        else:
            logging.warning('\nWarning: No template available. Template test not implemented.')
        # test context
        for item in self.context_list:
            self.assertIn(item, response.context.keys())

    def test_view_function(self):
        '''
            Tests url resolves to view function.
        '''
        if not self.view_function:
            raise ImproperlyConfigured('No view function available. Please provide a view_function.')
        match = resolve(self.test_url)
        self.assertEquals(self.view_function.__name__, match.func.__name__)

    def test_queryset(self):
        '''
            Tests if response context has the expected queryset.
        '''
        if not self.model_factory:
            raise ImproperlyConfigured('No model factory available. Please provide a model_factory.')
        self.model_factory.create_batch(5)
        qs = self.model.objects.all()
        response = self.client.get(self.test_url)
        context_qs = response.context[self.object_list_name]
        self.assertQuerysetEqual(qs, context_qs, ordered=False)