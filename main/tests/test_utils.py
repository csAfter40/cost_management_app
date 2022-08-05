from django.test.testcases import TestCase
from main.utils import(
    get_latest_transactions,
)
from main.tests.factories import (
    UserFactoryNoSignal,
    AccountFactory,
    TransactionFactory
)
import datetime
from datetime import timedelta

class TestUtilityFunctions(TestCase):
    def setUp(self):
       self.user = UserFactoryNoSignal()

    def test_get_latest_transactions(self):
        today = datetime.date.today()
        user_account = AccountFactory(user=self.user)
        TransactionFactory.create_batch(10)
        for i in range(10):
            TransactionFactory.create(account=user_account, category__is_transfer=False, date=(today-timedelta(days=i)))
            TransactionFactory.create(account=user_account, category__is_transfer=True, date=(today-timedelta(days=i)))
        queryset = get_latest_transactions(self.user, 5)
        self.assertEquals(len(queryset), 5)
        for i, object in enumerate(queryset):
            self.assertEquals(object.account.user, self.user)
            self.assertFalse(object.category.is_transfer)
            if i < len(queryset)-1:
                self.assertGreater(object.date, queryset[i+1].date)
