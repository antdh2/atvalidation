import unittest
from selenium import webdriver

class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_visitor_landing_on_homepage(self):
        # Ant has heard about a cool new input validation app
        # He goes to it's homepage
        self.browser.get('http://localhost:8000')
        # He notices the page title mentions the autotask app
        self.assertIn('123', self.browser.title)

if __name__ == '__main__':
    unittest.main(warnings='ignore')
