import logging
import difflib
from tqdm import tqdm

logger = logging.getLogger(__name__)


def get_urls_from_artist_name(browser, list_artist):
    list_urls = []
    base_url = "https://rateyourmusic.com"
    for index, artist in tqdm(enumerate(list_artist, 1), dynamic_ncols=True):
        artist = artist.replace(' ', '+')
        url = f"{base_url}/search?searchtype=a&searchterm={artist}"
        logger.debug("Searching %s in url %s", artist, url)
        browser.get_url(url)
        soup = browser.get_soup()
        url_artist = f"{base_url}{soup.find('a', {'class': 'searchpage'})['href']}"
        logger.debug("url for %s found : %s", artist, url_artist)
        list_urls.append(url_artist)
    return list_urls


def get_urls_from_album_name(browser, list_albums):
    list_urls = []
    list_artists = [x[0] for x in list_albums]
    list_albums_name = [x[1] for x in list_albums]
    list_artists_url = get_urls_from_artist_name(browser, list_artists)

    for index, url in tqdm(enumerate(list_artists_url, 0), dynamic_ncols=True):
        album_name = list_albums_name[index]
        logger.debug("Searching for %s at %s", album_name, url)
        browser.get_url(url)
        soup = browser.get_soup()
        artist_album_list = [[x.text.strip(), "https://rateyourmusic.com" + x.find('a')['href']] for x in soup.find_all('div', {'class': 'disco_mainline'})]
        artist_album_url = [x[1] for x in artist_album_list]
        artist_album_name = [x[0] for x in artist_album_list]
        
        # best_match = difflib.get_close_matches(album_name, album_name_artist)
        url_match = artist_album_url[artist_album_name.index(difflib.get_close_matches(album_name, artist_album_name)[0])]
        logger.debug("Best match : %s", url_match)
        list_urls.append(url_match)
    return list_urls
