from test_plus.test import TestCase
import factory
from django.db.models import signals

class TestCreateAccountView(TestCase):
    # decorator prevents user preferences object creation by signals.
    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def get_user(self):
        return self.make_user()

    def test_unauthenticated_access(self):
        self.assertLoginRequired('main:create_account')

    def test_get(self):
        user = self.get_user()
        with self.login(username=user.username):
            self.get_check_200('main:create_account')
