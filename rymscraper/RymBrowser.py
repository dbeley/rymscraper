from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import logging
import time

logger = logging.getLogger(__name__)


class RymBrowser(webdriver.Firefox):
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
            # Click on the cookie bar if found.
            if len(self.find_elements_by_class_name("as-oil__btn-optin")) > 0:
                self.find_element_by_class_name("as-oil__btn-optin").click()
                logger.debug("Cookie bar found. Clicking on ok.")
            # Click on the consent popu if found.
            if len(self.find_elements_by_class_name("fc-cta-consent")) > 0:
                self.find_element_by_class_name("fc-cta-consent").click()
                logger.debug("Consent popup found. Clicking on ok.")
            # Show all releases by clicking on all "Show all" links.
            try:
                for index, link in enumerate(
                    self.find_elements_by_class_name("disco_expand_section_link")
                ):
                    self.execute_script(
                        f"document.getElementsByClassName('disco_expand_section_link')[{index}].scrollIntoView(true);"
                    )
                    link.click()
                    time.sleep(0.2)
            except Exception as e:
                logger.debug('No "Show all" links found : %s.', e)
            # Test if IP is banned.
            if self.is_ip_banned():
                logger.error(
                    "IP banned from rym. Can't do any requests to the website. Exiting."
                )
                self.quit()
                exit()
            # Test if browser is rate-limited.
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
