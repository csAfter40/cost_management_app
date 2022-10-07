from selenium import webdriver
import unittest
from django.urls import reverse
from django.test import LiveServerTestCase

@unittest.skip('skip due to test duration')
class FuncTestLogin(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Firefox()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self) -> None:
        self.url = self.live_server_url + reverse('main:login')

    def test_page_has_title(self):
        self.browser.get(self.url)
        assert 'Login' in self.browser.title

if __name__ == '__main__':
    unittest.main()