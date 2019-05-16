from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import logging

logger = logging.getLogger(__name__)


class Rym_browser(webdriver.Firefox):
    def __init__(self, headless=True):
        logger.debug("rym_browsser init : headless = %s", headless)
        self.options = Options()
        if headless:
            self.options.headless = True

        webdriver.Firefox.__init__(self, options=self.options)

    def get_ddg(self):
        self.get("https://www.duckduckgo.fr")

    def restart(self):
        self.quit()
        # browser = webdriver.Firefox()
        webdriver.Firefox.__init__(self, options=self.options)

    def get_url(self, url):
        # url = self.current_url
        logger.debug('get_soup(browser, %s)', url)
        self.get(str(url))
        # if cookie bar found, click on the ok button
        try:
            self.find_element_by_class_name('as-oil__btn-optin').click()
            logger.debug("Cookie bar found. Clicking on ok.")
        except Exception as e:
            logger.debug("Cookie bar not found, %s", str(e).strip())
        logger.debug("browser.get(%s)", url)

    def get_soup(self):
        return BeautifulSoup(self.page_source, 'lxml')

    def is_rate_limited(self):
        while True:
            try:
                # logger.debug("Test ratelimit")
                # rate-limit
                if self.get_soup().find('form', {'id': 'sec_verify'}):
                    logger.error("Rate-limit detected. Restarting browser at %s", self.current_url)
                    self.restart()
                    return True
                else:
                    # logger.debug("No ratelimit")
                    return False
            except Exception as e:
                logger.error("Error scraping page %s : %s", self.current_url, e)
                return False
