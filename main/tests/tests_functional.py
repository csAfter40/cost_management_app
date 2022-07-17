from selenium import webdriver
import unittest
from django.urls import reverse
from wallet.settings import TESTING_HOST

class FuncTestLogin(unittest.TestCase):
    def setUp(self) -> None:
        self.browser = webdriver.Firefox()
        self.url = TESTING_HOST + reverse('main:login')

    def tearDown(self) -> None:
        self.browser.quit()
    
    def test_page_has_title(self):
        self.browser.get(self.url)
        assert 'Login' in self.browser.title

if __name__ == '__main__':
    unittest.main()