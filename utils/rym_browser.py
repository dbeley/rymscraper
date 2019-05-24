from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import logging

logger = logging.getLogger(__name__)


class Rym_browser(webdriver.Firefox):
    def __init__(self, headless=True):
        logger.debug("Starting Selenium Browser : headless = %s", headless)
        self.options = Options()
        if headless:
            self.options.headless = True

        webdriver.Firefox.__init__(self, options=self.options)

    def restart(self):
        self.quit()
        webdriver.Firefox.__init__(self, options=self.options)

    def get_url(self, url):
        logger.debug("get_url(browser, %s)", url)
        while True:
            self.get(str(url))
            # if cookie bar found, click on the ok button
            try:
                self.find_element_by_class_name("as-oil__btn-optin").click()
                logger.debug("Cookie bar found. Clicking on ok.")
            except Exception as e:
                logger.debug("Cookie bar not found, %s", e)
            if self.is_ip_banned():
                logger.error(
                    "IP banned from rym. Can't do any requests to the website. Exiting."
                )
                self.quit()
                exit()
            if self.is_rate_limited():
                logger.error("Rate-limit detected. Restarting browser.")
                self.restart()
            else:
                break
        return

    def get_soup(self):
        return BeautifulSoup(self.page_source, "lxml")

    def is_ip_banned(self):
        logger.debug("soup.title : %s", self.get_soup().title)
        return self.get_soup().title.text.strip() == "IP blocked"

    def is_rate_limited(self):
        return self.get_soup().find("form", {"id": "sec_verify"})
