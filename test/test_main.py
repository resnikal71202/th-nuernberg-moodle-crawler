import unittest
from unittest.mock import MagicMock, patch

import selenium
from bs4 import BeautifulSoup

from src import __main__ as main


class TestMain(unittest.TestCase):
    def test_get_options(self):
        """
        tests if the options are of type selenium.webdriver.firefox.options()
        """
        crawler = main.Crawler("")
        assert isinstance(
            crawler.get_options(), selenium.webdriver.firefox.options.Options
        )

    @patch("src.__main__.webdriver")
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

    @patch("src.__main__.webdriver")
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

    @patch("src.__main__.webdriver")
    def test_test_for_pdf_no_pdf(self, mock_webdriver):
        """
        tests if the test_for_pdf() function works
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
        result = crawler.test_for_pdf(
            "https://short.moodle.net/mod/resource/view.php?id=1234"
        )

        assert result == ""

    @patch("src.__main__.webdriver")
    def test_test_for_pdf_no_pdf(self, mock_webdriver):
        """
        tests if the test_for_pdf() function works
        """
        crawler = main.Crawler("")
        crawler.driver = mock_webdriver.Firefox.return_value
        mock_instance = crawler.driver

        mock_get = MagicMock(name="get")
        mock_instance.get = mock_get

        mock_page_source = '<html><body><section id="region-main">\
            <a href="https://shortlink/to/a/small.pdf">Course Content</a>\
            </section></body></html>'

        mock_instance.page_source = mock_page_source

        # Call the function under test
        result = crawler.test_for_pdf(
            "https://shortlink/to/a/small.pdf"
        )

        assert (
            result
            == "https://shortlink/to/a/small.pdf"
        )

    @patch("src.__main__.webdriver")
    def test_get_pdfs(self, mock_webdriver):
        """
        tests if the get_pdfs() function works
        """
        crawler = main.Crawler("")
        crawler.driver = mock_webdriver.Firefox.return_value
        mock_instance = crawler.driver

        mock_get = MagicMock(name="get")
        mock_instance.get = mock_get

        mock_page_source = '<html><body><section id="region-main">\
            <a class="aalink" href="https://short.moodle/view.php?id=1">\
                Introduction to Moodle</a></section></body></html>'
        mock_instance.page_source = mock_page_source

        mock_get_course = MagicMock(name="get_course")
        mock_get_course.return_value = BeautifulSoup(mock_page_source,
                                                     "html.parser")
        crawler.get_course = mock_get_course

        mock_test_for_pdf = MagicMock(name="test_for_pdf")
        mock_test_for_pdf.return_value = "https://shortlink/to/a/small.pdf"
        crawler.test_for_pdf = mock_test_for_pdf

        # Call the function under test
        result = crawler.get_pdfs()

        assert result == [
            "https://shortlink/to/a/small.pdf"
        ]


if __name__ == "__main__":
    unittest.main()
