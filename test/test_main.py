import unittest
from unittest.mock import MagicMock, patch

import selenium
from bs4 import BeautifulSoup

from src import crawler as main


class TestMain(unittest.TestCase):
    def test_get_options(self):
        """
        tests if the options are of type selenium.webdriver.firefox.options()
        """
        crawler = main.Crawler("")
        assert isinstance(
            crawler.get_options(), selenium.webdriver.firefox.options.Options
        )

    @patch("src.crawler.webdriver")
    def test_login(self, mock_webdriver):
        """
        tests if the login works
        """
        crawler = main.Crawler("")
        crawler.driver = mock_webdriver.Firefox.return_value
        mock_instance = crawler.driver
        mock_instance.current_url = "https://school.moodledemo.net/dashboard"
        mock_get = MagicMock(name="get")
        mock_instance.get = mock_get
        crawler.login(
            "https://school.moodledemo.net/login/index.php",
            "student",
            "moodle"
        )
        mock_get.assert_called_with(
            "https://school.moodledemo.net/login/index.php")

    @patch("src.crawler.webdriver")
    def test_get_course(self, mock_webdriver):
        """
        tests the get_course() function
        """
        crawler = main.Crawler("")
        crawler.driver = mock_webdriver.Firefox.return_value
        mock_instance = crawler.driver

        mock_get = MagicMock(name="get")
        mock_instance.get = mock_get

        mock_page_source = '<html><body><section id="region-main">\
            Course Content</section></body></html>'
        mock_instance.page_source = mock_page_source

        # Call the function under test
        result = crawler.get_course()

        soup = BeautifulSoup(mock_page_source, "html.parser")
        expected_result = soup.find("section", id="region-main")
        # Assertions
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
