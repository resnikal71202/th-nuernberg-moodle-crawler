import argparse
import configparser
import os
import re
import urllib.parse

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


class Crawler:
    def get_options(self) -> Options:
        """
        get the options for the webdriver
        returns:
            Options: the options for the webdriver
        """
        options = Options()
        options.add_argument("-headless")
        return options

    def login(self, url: str, username: str, password: str) -> bool:
        """
        Log in to the moodle page
        args:
            url: the url of the moodle page
            username: the username
            password: the password
        returns:
            bool: True if the login was successful, False if not
        """
        self.driver.get(url)
        username_input = self.driver.find_element(by=By.ID, value="username")
        username_input.send_keys(username)
        password_input = self.driver.find_element(by=By.ID, value="password")
        password_input.send_keys(password)
        loginbtn = self.driver.find_element(by=By.ID, value="loginbtn")
        loginbtn.click()
        self.driver.implicitly_wait(10)
        if "login" in self.driver.current_url:
            return False
        return True

    def get_course(self) -> any:
        """
        get the course
        returns:
            BeautifulSoup.Tag
            BeautifulSoup.NavigableString
            None
        """
        self.driver.get(self.url)
        # Wait for the page to load
        self.driver.implicitly_wait(10)
        # Get the page source
        page = self.driver.page_source
        # Parse the page
        soup = BeautifulSoup(page, "html.parser")
        # get region-main
        region_main = soup.find("section", id="region-main")
        return region_main

    def get_download_links(self, region_main):
        download_links = []
        aalinks = region_main.find_all("a", class_="aalink stretched-link")
        for link in aalinks:
            span_tag = link.find("span", class_="accesshide")
            if span_tag and "Forum" in span_tag.get_text():
                continue
            download_links.append(link["href"])
        return download_links

    def download_files(self, download_links):
        cookies = self.driver.get_cookies()

        for link in download_links:
            # Send a HEAD request to get headers including Content-Disposition
            if link.lower().startswith("https://"):
                response = requests.head(
                    link,
                    allow_redirects=True,
                    cookies={cookie["name"]: cookie["value"] for cookie in cookies},
                )
            else:
                response = requests.head(link, allow_redirects=True)

            # Extract filename from Content-Disposition header if available
            content_disposition = response.headers.get("Content-Disposition")
            if content_disposition and "filename" in content_disposition:
                filename = re.findall('filename="(.+)"', content_disposition)[0]
            else:
                # If Content-Disposition header is not present, extract filename from URL
                filename = os.path.basename(
                    urllib.parse.unquote(urllib.parse.urlsplit(link).path)
                )

            # Get the actual file content using a GET request
            response = requests.get(
                link,
                cookies={cookie["name"]: cookie["value"] for cookie in cookies},
                stream=True,
            )

            # Specify the local path to save the downloaded file
            local_path = os.path.join("downloads", filename)

            # Write the file to disk
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

    def __init__(self, url: str) -> None:
        self.url = url

    def destruct(self) -> None:
        """
        destruct the crawler
        """
        self.driver.quit()

    def __del__(self) -> None:
        self.destruct()


def main() -> None:
    """
    Main function
    """
    # comand line arguments
    parser = argparse.ArgumentParser(description="Download pdfs from moodle")
    parser.add_argument("--username", type=str, help="the username")
    parser.add_argument("--password", type=str, help="the password")
    args = parser.parse_args()

    # read config
    config = configparser.ConfigParser()
    config.read("config.ini")
    args.url_login = config["moodle"]["url_login"]
    args.url_course = config["course"]["url"]

    # create crawler
    crawler = Crawler(args.url_course)
    # get options
    options = crawler.get_options()
    # create driver
    crawler.driver = webdriver.Firefox(options=options)
    # login
    crawler.login(args.url_login, args.username, args.password)

    # get download links
    region_main = crawler.get_course()
    download_links = crawler.get_download_links(region_main)
    crawler.download_files(download_links)

    return


if __name__ == "__main__":
    main()
