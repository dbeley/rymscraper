import logging
from typing import List, Dict
from rymscraper import RymBrowser, utils

logger = logging.getLogger(__name__)
__version__ = "0.1"
name = "rymscraper"


class RymNetwork:
    """Class RymNetwork."""

    def __init__(self, headless: bool = True):
        self.browser = RymBrowser.RymBrowser(headless=headless)

    def get_album_infos(self, url: str = None, name: str = None) -> Dict:
        """Returns a dict containing infos for an album.

        Parameters:
            url: Url of the album.
            name: Name of the album in the "Artist - Album" format.

        Returns:
            album_info: Dict containing album informations.

        """
        if name:
            url = utils.get_url_from_album_name(self.browser, name)
        if not url:
            raise Exception("Invalid url or name. Exiting.")

        self.browser.get_url(url)
        album_infos = utils.get_album_infos(self.browser.get_soup())
        return album_infos

    def get_albums_infos(
        self, urls: List[str] = None, names: List[str] = None
    ) -> List[Dict]:
        """Returns a list of dicts containing infos from several albums."""
        if names:
            list_albums_infos = [self.get_album_infos(name=x) for x in names]
        elif urls:
            list_albums_infos = [self.get_album_infos(url=x) for x in urls]
        else:
            raise Exception("No list of urls or names entered. Exiting.")

        return list_albums_infos

    def get_artist_infos(self, url: str = None, name: str = None) -> Dict:
        """Returns a dict containing artist infos."""
        if name:
            url = utils.get_url_from_artist_name(self.browser, name)
        if not url:
            raise Exception("Invalid url or name. Exiting.")

        self.browser.get_url(url)
        artist_infos = utils.get_artist_infos(self.browser.get_soup())
        return artist_infos

    def get_artists_infos(
        self, urls: List[str] = None, names: List[str] = None
    ) -> List[Dict]:
        """Returns a list of dicts containing infos from several artists."""
        if names:
            list_artists_infos = [self.get_artist_infos(name=x) for x in names]
        elif urls:
            list_artists_infos = [self.get_artist_infos(url=x) for x in urls]
        else:
            raise Exception("No list of urls or names entered. Exiting.")

        return list_artists_infos

    def get_chart_infos(self, url: str = None) -> List[Dict]:
        """Returns a list of dicts containing chart infos.

        Parameters:
            url: An url for a chart. Can be created with the RymUrl helper.
            See the get_chart.py script in the examples folder for an example.

        Returns:
            list_rows: List of dicts for each rows from the chart.

        """
        list_rows = []
        while True:
            try:
                self.browser.get_url(url)
                logger.info("Extracting chart rows for url %s", url)
                soup = self.browser.get_soup()

                # table containing albums
                if soup.find("table", {"class": "mbgen"}):
                    logger.debug("Table class mbgen found")
                    table = soup.find("table", {"class": "mbgen"})
                    rows = table.find_all("tr")
                    if len(rows) == 0:
                        logger.debug("No rows extracted. Exiting")
                        break
                    for row in rows:
                        # don't parse ads
                        if not row.find("script"):
                            dict_row = utils.get_chart_row_infos(row)
                            list_rows.append(dict_row)
                else:
                    logger.warning("Table class mbgen not found")
                    break

                # link to the next page
                if soup.find("a", {"class": "navlinknext"}):
                    logger.debug("Next page found")
                    url.page += 1
                    soup.decompose()
                    try:
                        self.browser.get_url(url)
                        soup = self.browser.get_soup()
                    except Exception as e:
                        logger.error(e)
                        break
                else:
                    logger.debug("No next page found. Exiting.")
                    break
            except Exception as e:
                logger.error("Error scraping page %s : %s", url, e)
                break

        return list_rows

    def get_discography_infos(
        self,
        url: str = None,
        name: str = None,
        complementary_infos: bool = False,
    ) -> List[Dict]:
        """Returns a list of dict containing discography infos."""
        if name:
            url = utils.get_url_from_artist_name(self.browser, name)
        if not url:
            raise Exception("Invalid url or name. Exiting.")

        self.browser.get_url(url)
        artist_disco = utils.get_artist_disco(
            self.browser, url, complementary_infos
        )
        return artist_disco

    def get_discographies_infos(
        self,
        urls: List[str] = None,
        names: List[str] = None,
        complementary_infos: bool = False,
    ) -> List[Dict]:
        """Returns a list of dicts containing infos from several discographies."""
        if names:
            list_artists_discos = []
            for name in names:
                artist_disco = self.get_discography_infos(
                    name=name, complementary_infos=complementary_infos
                )
                list_artists_discos.extend(artist_disco)

            # list_artists_discos = [
            #     self.get_discography_infos(
            #         name=x, complementary_infos=complementary_infos
            #     )
            #     for x in names
            # ]
        elif urls:
            for url in urls:
                artist_disco = self.get_discography_infos(
                    url=url, complementary_infos=complementary_infos
                )
                list_artists_discos.extend(artist_disco)
            # list_artists_discos = [
            #     self.get_discography_infos(
            #         url=x, complementary_infos=complementary_infos
            #     )
            #     for x in urls
            # ]
        else:
            raise Exception("No list of urls or names entered. Exiting.")

        return list_artists_discos
