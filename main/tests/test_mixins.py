import logging
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import AnonymousUser
from django.urls import resolve


class BaseViewTestMixin(object):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_url = None # str
        cls.redirect_url = None # str 
        cls.context_list = None # List of strings
        cls.template = None # str 'app_name/template_name.html'
        cls.post_method = False
        cls.get_method = True
        cls.post_data = None # List of dictionaries
        cls.view_function = None # Add .as_view()
        cls.login_required = False # bool
        cls.user_factory = None

    def setUp(self) -> None:
        self.user = self.get_user()
        if self.test_url==None:
            raise ImproperlyConfigured('No test url available. Please provide a test_url')
        if self.login_required:
            self.client.force_login(self.user)

    def get_user(self):
        user = self.user_factory() if self.user_factory else AnonymousUser()
        return user

    def test_unauthenticated_access(self):
        '''
            Tests unauthenticated access in case view has LoginRequired mixin.
        '''
        if not self.login_required:
            return
        self.client.logout()
        if self.get_method:
            response = self.client.get(self.test_url)
        else:
            response = self.client.post(self.test_url, self.post_data)
        self.assertEquals(response.status_code, 302)

    def test_get(self):    
        '''
            Tests get request response has status 200 and 
            response context has expected keys.
        ''' 
        if not self.get_method:
            return
        response = self.client.get(self.test_url)
        self.assertEquals(response.status_code, 200)
        # test template
        if self.template:
            self.assertTemplateUsed(response, self.template)
        else:
            logging.warning('\nWarning: No template available. Template test not implemented.')
        # test context
        if self.context_list == []:
            pass
        elif self.context_list:
            for item in self.context_list:
                self.assertIn(item, response.context.keys())
        else:
            logging.warning('\nWarning: No context_list available. Context test not implemented.')

    def test_post(self):
        if not self.post_method:
            return
        response = self.client.post(self.test_url, self.post_data)
        if self.redirect_url:
            self.assertRedirects(response, self.redirect_url, 302, fetch_redirect_response=False)
        else:
            self.assertEquals(response.status_code, 200)
        return response

    def test_view_function(self):
        '''
            Tests url resolves to view function.
        '''
        if not self.view_function:
            raise ImproperlyConfigured('No view function available. Please provide a view_function.')
        match = resolve(self.test_url)
        self.assertEquals(self.view_function.__name__, match.func.__name__)


class UserFailTestMixin(BaseViewTestMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.object = None

    def test_user_fail_test(self):
        '''
            Tests if permission denied when user tries to access an object
            that does not belong to user.
        '''
        if not self.object:
            raise ImproperlyConfigured('No object available. Please provide a test object.')
        new_user = self.user_factory()
        self.object.user = new_user
        self.object.save()
        if self.get_method:
            response = self.client.get(self.test_url)
        else:
            response = self.client.post(self.test_url, self.post_data)
        self.assertEquals(response.status_code, 403)