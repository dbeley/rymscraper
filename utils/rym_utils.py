import logging

logger = logging.getLogger(__name__)


def get_urls_from_artists_name(browser, list_artists):
    list_urls = []
    base_url = "https://rateyourmusic.com"
    for index, artist in enumerate(list_artists, 1):
        artist = artist.replace(' ', '+')
        url = f"{base_url}/search?searchtype=a&searchterm={artist}"
        logger.debug("Searching %s in url %s", artist, url)
        browser.get_url(url)
        soup = browser.get_soup()
        url_artist = f"{base_url}{soup.find('a', {'class': 'searchpage'})['href']}"
        logger.info("%s found : %s", artist, url_artist)
        list_urls.append(url_artist)
    return list_urls
