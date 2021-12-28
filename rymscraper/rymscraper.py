import logging
from typing import List, Dict, Optional
from . import RymBrowser, RymUrl, utils

logger = logging.getLogger(__name__)


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

        logger.info("Extracting album informations for %s.", url)
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

    def get_album_timeline(self, url: str = None, name: str = None) -> List[dict]:
        """Returns a dict containing timeline for an album.

        Parameters:
            url: Url of the album.
            name: Name of the album in the "Artist - Album" format.

        Returns:
            album_timeline: Dict containing album timeline.

        """
        if name:
            url = utils.get_url_from_album_name(self.browser, name)
        if not url:
            raise Exception("Invalid url or name. Exiting.")

        logger.info("Extracting album timeline for %s.", url)
        self.browser.get_url(url)
        album_infos = utils.get_album_timeline(self.browser)
        return album_infos

    def get_albums_timeline(
        self, urls: List[str] = None, names: List[str] = None
    ) -> List[List[Dict]]:
        """Returns a list of dicts containing timeline from several albums."""
        if names:
            list_albums_timeline = [self.get_album_timeline(name=x) for x in names]
        elif urls:
            list_albums_timeline = [self.get_album_timeline(url=x) for x in urls]
        else:
            raise Exception("No list of urls or names entered. Exiting.")
        return list_albums_timeline

    def get_artist_infos(self, url: str = None, name: str = None) -> Dict:
        """Returns a dict containing artist infos."""
        if name:
            url = utils.get_url_from_artist_name(self.browser, name)
        if not url:
            raise Exception("Invalid url or name. Exiting.")

        logger.info("Extracting artist informations for %s.", url)
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

    def get_chart_infos(
        self, url: Optional[str] = None, max_page: int = None
    ) -> List[Dict]:
        """Returns a list of dicts containing chart infos.

        Parameters:
            url: An url for a chart. Can be created with the RymUrl helper.
            See the get_chart.py script in the examples folder for an example.
            max_page: The max number of pages to extract from the chart.

        Returns:
            list_rows: List of dicts for each rows from the chart.

        """
        logger.info("Extracting chart informations for %s.", url)

        list_rows = []
        while True:
            try:
                self.browser.get_url(url)
                logger.debug("Extracting chart rows for url %s", url)
                soup = self.browser.get_soup()

                # table containing albums
                if soup.find(
                    "div", {"class": "chart_results chart_results_ charts_page"}
                ):
                    logger.debug("Table class mbgen found")
                    table = soup.find(
                        "div", {"class": "chart_results chart_results_ charts_page"}
                    )
                    rows = table.find_all(
                        "div", {"class": "topcharts_itembox chart_item_release"}
                    )
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
                if soup.find("a", {"class": "ui_pagination_next"}):
                    logger.debug("Next page found")
                    if max_page and url.page == max_page:
                        break
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

        logger.info("Extracting discography informations for %s.", url)
        self.browser.get_url(url)
        artist_disco = utils.get_artist_disco(
            self.browser, self.browser.get_soup(), complementary_infos
        )
        return artist_disco

    def get_discographies_infos(
        self,
        urls: List[str] = None,
        names: List[str] = None,
        complementary_infos: bool = False,
    ) -> List[Dict]:
        """Returns a list of dicts containing infos from several discography."""
        list_artists_discos = []
        if names:
            for name in names:
                artist_disco = self.get_discography_infos(
                    name=name, complementary_infos=complementary_infos
                )
                list_artists_discos.extend(artist_disco)
        elif urls:
            for url in urls:
                artist_disco = self.get_discography_infos(
                    url=url, complementary_infos=complementary_infos
                )
                list_artists_discos.extend(artist_disco)
        else:
            raise Exception("No list of urls or names entered. Exiting.")

        return list_artists_discos
