from selenium import webdriver
import unittest
from django.urls import reverse
from django.test import LiveServerTestCase

class FuncTestLogin(LiveServerTestCase):
    def setUp(self) -> None:
        self.browser = webdriver.Firefox()
        self.url = self.live_server_url + reverse('main:login')

    def tearDown(self) -> None:
        self.browser.quit()
    
    def test_page_has_title(self):
        self.browser.get(self.url)
        assert 'Login' in self.browser.title

if __name__ == '__main__':
    unittest.main()