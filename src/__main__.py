import argparse
import configparser
import datetime
import json
import os
import shutil
import time
import urllib.parse

import PyPDF2
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
        options.set_preference(
            "browser.download.folderList", 2)
        options.set_preference(
            "browser.download.dir", os.getcwd() + "/downloads")
        options.set_preference(
            "browser.download.useDownloadDir", True)
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk", "application/pdf")
        options.set_preference(
            "pdfjs.disabled", True)
        options.set_preference(
            "browser.download.manager.\
                               showWhenStarting",
            False,
        )
        options.set_preference(
            "browser.download.manager.\
                               focusWhenStarting",
            False,
        )
        options.set_preference(
            "browser.download.manager.\
                               alertOnEXEOpen",
            False,
        )
        options.set_preference(
            "browser.download.manager.\
                               showAlertOnComplete",
            False,
        )
        options.set_preference(
            "browser.download.manager.\
                               closeWhenDone",
            True,
        )
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

    def test_for_pdf(self, url) -> str:
        """
        tests if the url contains an pdf
        args:
            url: the url
        returns:
            str: the pdf url
        """
        self.driver.get(url)
        # Wait for the page to load
        self.driver.implicitly_wait(10)
        # Get the page source
        page = self.driver.page_source
        # Parse the page
        soup = BeautifulSoup(page, "html.parser")
        # get region-main
        region_main = soup.find("section", id="region-main")
        # get all links
        links = region_main.find_all("a")
        for link in links:
            if not link["href"].endswith(".pdf"):
                continue
            return link["href"]
        return ""

    def get_pdfs(self) -> str:
        """
        get the pdfs
        returns:
            list: the pdfs
        """
        # get all aalinks
        a_tags = self.get_course().find_all(
            "a", class_="aalink"
        )  # find all <a> tags with class 'aalink'
        pdfs = []
        for a in a_tags:
            pdf = self.test_for_pdf(a["href"])
            if pdf != "":
                pdfs.append(pdf)
        return pdfs

    def download_pdfs(self, pdfs: list) -> None:
        """
        download the pdfs
        args:
            pdfs: the pdfs
        returns:
            None
        """
        for pdf in pdfs:
            # Open a new window to download the file
            self.driver.execute_script(
                f"window.open('{pdf}', '_blank', 'width=800,height=600');"
            )
            # wait for the download to finish
            self.driver.implicitly_wait(10)
            # Switch back to the main window or tab
            self.driver.switch_to.window(self.driver.window_handles[0])

    def __init__(self, url: str) -> None:
        self.url = url

    def destruct(self) -> None:
        """
        destruct the crawler
        """
        self.driver.quit()

    def __del__(self) -> None:
        self.destruct()

    def search_json(self, url: str) -> str:
        """
        searches the json for the pdfs and the place where they are stored
        args:
            url: the url of the pdf
        returns:
            str: the path to the pdf
        """
        pdfs = json.load(open("pdfs.json", "r"))
        for pdf in pdfs["pdfs"]:
            if pdf["url"] == url:
                return pdf["path"]
        return "unknown"

    def fill_json(self, name: str, url: str, path: str) -> None:
        """
        fills the json with the pdfs
        args:
            name: the name of the pdf
            url: the url of the pdf
            path: the path to the pdf
        returns:
            None
        """
        pdfs = json.load(open("pdfs.json", "r"))
        # check if url is already in the json
        for pdf in pdfs["pdfs"]:
            if pdf["url"] == url:
                return
        # add the pdf to the json
        pdfs["pdfs"].append({"name": name, "url": url, "path": path})
        json.dump(pdfs, open("pdfs.json", "w"))
        return

    def move_pdf(self, name: str, url: str, path: str) -> None:
        """
        moves the pdf to the right folder according to the json
        """
        # get the path to the downloads folder in this folder
        downloads_path = os.path.join(os.getcwd(), "downloads", name)
        # check if folder exists and create it if not
        if not os.path.exists(path):
            os.makedirs(path)
        # get the creation date of the pdf
        last_change = PyPDF2.PdfReader(downloads_path).metadata.creation_date
        # convert the date to a string
        last_change = last_change.strftime("%Y-%m-%d_%H-%M-%S")
        # strip .pdf from the name
        name = name.replace(".pdf", "")
        # append the last change to the name
        name = name + "_" + last_change + ".pdf"
        # get the path to the destination folder
        path = os.path.join(os.getcwd(), path, name)
        # remove the file if it already exists
        if os.path.exists(path):
            os.remove(downloads_path)
        else:
            # move the pdf
            shutil.move(downloads_path, path)
        return


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

    # get pdfs
    pdfs = crawler.get_pdfs()

    # download pdfs
    crawler.download_pdfs(pdfs)

    # wait for the downloads to finish
    time.sleep(3)

    # move pdfs
    for pdf in pdfs:
        name = urllib.parse.unquote(pdf.split("/")[-1])
        path = crawler.search_json(pdf)
        crawler.move_pdf(name, pdf, path)
        crawler.fill_json(name, pdf, path)

    return


if __name__ == "__main__":
    main()
