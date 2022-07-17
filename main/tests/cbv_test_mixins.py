from django.db import models


class TestCreateViewMixin(object):

    test_url_pattern = None
    success_url = None
    model = None
    data = None
    context_list = None

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
            self.get_check_200(self.test_url_pattern)
        # test context
        for item in self.context_list:
            self.assertInContext(item)

    def test_post_success(self):
        print(self.data)
        with self.login(self.user):
            response = self.post(self.test_url_pattern, data=self.data)
        # test response code
        self.response_302(response)
        # test created object
        object = self.get_object()
        for key, value in self.data.items():
            if isinstance(getattr(object, key), models.Model):
                assert getattr(object, key).id == value
            else:
                assert getattr(object, key) == value
        # assert object.name == data['name']
        assert object.user == self.user
        # test redirect link
        assert self.success_url in response.get('Location')