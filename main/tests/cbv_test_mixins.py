from django.db import models


class TestCreateViewMixin(object):

    test_url_pattern = None
    success_url = None
    model = None
    valid_data = None
    invalid_data = None
    context_list = None
    template_name = None

    def setUp(self) -> None:
        self.user = self.get_user()

    def get_user(self):
        return self.make_user()

    def get_object(self):
        return self.model.objects.all().first()

    def test_unauthenticated_access(self):
        self.assertLoginRequired(self.test_url_pattern)

    def test_get(self):
        with self.login(self.user):
            response = self.get(self.test_url_pattern)
            assert response.status_code == 200
            assert response.template_name[0] == self.template_name
            self.get_check_200(self.test_url_pattern)
        # test context
        for item in self.context_list:
            self.assertInContext(item)

    def test_post_success(self):
        with self.login(self.user):
            response = self.post(self.test_url_pattern, data=self.valid_data)
        # test response code
        self.response_302(response)
        # test created object
        valid_object = self.get_object()
        assert valid_object != None
        for key, value in self.valid_data.items():
            if isinstance(getattr(valid_object, key), models.Model):
                assert getattr(valid_object, key).id == value
            else:
                assert getattr(valid_object, key) == value
        assert valid_object.user == self.user
        # test redirect link
        assert self.success_url in response.get('Location')

    def test_post_failure(self):
        with self.login(self.user):
            response = self.post(self.test_url_pattern, data=self.invalid_data)
        # test response code
        self.response_200(response)
        # test created object
        invalid_object = self.get_object()
        assert invalid_object == None
