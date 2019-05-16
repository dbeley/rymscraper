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
        logger.debug('get_url(browser, %s)', url)
        self.get(str(url))
        # if cookie bar found, click on the ok button
        # try:
        #     self.find_element_by_class_name('as-oil__btn-optin').click()
        #     logger.debug("Cookie bar found. Clicking on ok.")
        # except Exception as e:
        #     logger.debug("Cookie bar not found, %s", str(e).strip())
        return BeautifulSoup(self.page_source, 'lxml')

    def get_soup(self):
        return BeautifulSoup(self.page_source, 'lxml')

    def is_ip_banned(self):
        logger.debug("soup.title : %s", self.get_soup().title)
        return self.get_soup().title.text.strip() == 'IP blocked'

    def is_rate_limited(self):
        try:
            # rate-limit
            if self.get_soup().find('form', {'id': 'sec_verify'}):
                logger.error("Rate-limit detected. Restarting browser at %s", self.current_url)
                self.restart()
                return True
            else:
                return False
        except Exception as e:
            logger.error("Error scraping page %s : %s", self.current_url, e)
            return False
