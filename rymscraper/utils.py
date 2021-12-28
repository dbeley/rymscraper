import logging
import re
import time
import difflib
from tqdm import tqdm
from bs4 import BeautifulSoup, NavigableString, element
from selenium.webdriver.common.by import By
from typing import List

logger = logging.getLogger(__name__)


def get_close_matches_icase(word, possibilities, *args, **kwargs):
    """Case-insensitive version of difflib.get_close_matches"""
    lword = word.lower()
    lpos = {p.lower(): p for p in possibilities}
    lmatch = difflib.get_close_matches(lword, lpos.keys(), *args, **kwargs)
    return [lpos[m] for m in lmatch]


def get_url_from_artist_name(browser, artist: str) -> str:
    """Returns the url of the first result for an name on rateyourmusic."""
    base_url = "https://rateyourmusic.com"
    artist = artist.strip().replace(" ", "+")
    url = f"{base_url}/search?searchtype=a&searchterm={artist}"
    logger.debug("Searching %s in url %s", artist, url)
    browser.get_url(url)
    soup = browser.get_soup()
    url_artist = f"{base_url}{soup.find('a', {'class': 'searchpage'})['href']}"
    logger.debug("url for %s found : %s", artist, url_artist)
    return url_artist


def get_url_from_album_name(browser, name: str) -> str:
    """Returns the url of an album."""
    album_name = name.split("-")[1].strip()
    artist_name = name.split("-")[0].strip()
    artist_url = get_url_from_artist_name(browser, artist_name)

    logger.debug("Searching for %s at %s", album_name, artist_url)
    browser.get_url(artist_url)
    soup = browser.get_soup()
    artist_album_list = [
        [x.text.strip(), "https://rateyourmusic.com" + x.find("a")["href"]]
        for x in soup.find_all("div", {"class": "disco_mainline"})
    ]
    artist_album_url = [x[1] for x in artist_album_list]
    artist_album_name = [x[0] for x in artist_album_list]

    url_match = artist_album_url[
        artist_album_name.index(
            get_close_matches_icase(album_name, artist_album_name)[0]
        )
    ]
    logger.debug("Best match : %s", url_match)
    return url_match


def get_album_infos(soup: BeautifulSoup) -> dict:
    """Returns a dict containing infos from an album."""
    album_infos = {
        "Name": soup.find("div", {"class": "album_title"}).text.split("\n")[0].strip(),
        "Artist": soup.find("div", {"class": "album_title"})
        .text.split("\n")[2]
        .strip()[3:],
    }

    album_complementary_infos = [
        [x.find("th").text.strip(), x.find("td").text.strip()]
        for x in soup.find("table", {"class": "album_info"}).find_all("tr")
    ]
    for info in album_complementary_infos:
        album_infos[info[0]] = info[1]

    try:
        del album_infos["Share"]
    except KeyError:
        pass

    album_infos["Track listing"] = [
        x.find("span", {"class": "tracklist_title"})
        .find("span", {"class": "rendered_text"})
        .text.strip()
        for x in soup.find("ul", {"id": "tracks"}).find_all("li")
        if x.find("span", {"class": "tracklist_title"})
    ]

    album_infos["Colorscheme"] = [
        re.split(";|:", x["style"])[1]
        for x in soup.find("table", {"class": "color_bar"}).find_all("td")
    ]

    return album_infos


def parse_catalog_line(row: element.Tag) -> dict:
    return {
        "Date": row.find("div", {"class": "catalog_date"}).text.strip(),
        "User": row.find("span", {"class": "catalog_user"}).text.strip(),
    }


def get_album_timeline(browser) -> List[dict]:
    """Returns a list of dict containing the timeline of the notes of an album."""
    catalog_list = []
    while True:
        soup = browser.get_soup()
        catalog_lines = soup.find(
            "div", {"class": "catalog_list", "id": "catalog_list"}
        )
        catalog_list += [
            parse_catalog_line(x)
            for x in catalog_lines.findAll("div", {"class": "catalog_line"})
        ]
        if (
            len(
                browser.find_element(By.CLASS_NAME, "catalog_section").find_elements(
                    By.CLASS_NAME, "navlinknext"
                )
            )
            == 0
        ):
            break
        browser.execute_script(
            "document.getElementsByClassName('navlinknext')[1].scrollIntoView(true);"
        )
        browser.find_element(By.CLASS_NAME, "catalog_section").find_element(
            By.CLASS_NAME, "navlinknext"
        ).click()
        logger.debug("Extracting timeline : %s items found.", len(catalog_list))
        time.sleep(2)
    return catalog_list


def get_artist_infos(soup: BeautifulSoup) -> dict:
    """Returns a dict containing infos from an artist."""
    artist_infos = {"Name": soup.find("h1", {"class": "artist_name_hdr"}).text.strip()}

    artist_infos_descriptors = [
        x.text.strip()
        for x in soup.find("div", {"class": "artist_info"}).find_all(
            "div", {"class": "info_hdr"}
        )
    ]
    artist_infos_values = [
        x.nextSibling.text.strip()
        for x in soup.find("div", {"class": "artist_info"}).find_all(
            "div", {"class": "info_hdr"}
        )
        # Ignore new follow button, will fill it later
        if not isinstance(x.nextSibling, NavigableString)
    ]
    # append number of followers
    artist_infos_values[-1] = (
        soup.find("span", {"class": "label_num_followers"})
        .text.replace(" followers", "")
        .replace(",", "")
    )
    for d, v in zip(artist_infos_descriptors, artist_infos_values):
        artist_infos[d] = v

    try:
        del artist_infos["Share"]
    except KeyError:
        pass

    return artist_infos


def get_chart_row_infos(row: element.Tag) -> dict:
    """Returns a dict containing infos from a chart row."""
    dict_row = {}
    try:
        dict_row["Rank"] = row.find(
            "div", {"class": "topcharts_position"}
        ).text.replace(".", "")
    except Exception as e:
        logger.error("Rank : %s", e)
        dict_row["Rank"] = "NA"
    try:
        dict_row["Artist"] = row.find("div", {"class": "topcharts_item_artist"}).text
    except Exception as e:
        logger.error("Artist: %s", e)
        dict_row["Artist"] = "NA"
    try:
        dict_row["Album"] = row.find("div", {"class": "topcharts_item_title"}).text
        logger.debug(
            "%s - %s - %s",
            dict_row["Rank"],
            dict_row["Artist"],
            dict_row["Album"],
        )
    except Exception as e:
        logger.error("Album : %s", e)
        dict_row["Album"] = "NA"
    try:
        dict_row["Date"] = (
            row.find("div", {"class": "topcharts_item_releasedate"})
            .text.replace("(", "")
            .replace(")", "")
            .strip()
        )
    except Exception as e:
        logger.error("Date : %s", e)
        dict_row["Date"] = "NA"
    try:
        dict_row["Genres"] = ", ".join(
            [
                x.text
                for x in row.find(
                    "div", {"class": "topcharts_item_genres_container"}
                ).find_all("a", {"class": "genre"})
            ]
        )
    except Exception as e:
        logger.error("Genres : %s", e)
        dict_row["Genres"] = "NA"
    try:
        dict_row["RYM Rating"] = row.find(
            "span", {"class": "topcharts_avg_rating_stat"}
        ).text
        dict_row["Ratings"] = row.find(
            "span", {"class": "topcharts_ratings_stat"}
        ).text.replace(",", "")
        dict_row["Reviews"] = row.find(
            "span", {"class": "topcharts_reviews_stat"}
        ).text.replace(",", "")
    except Exception as e:
        logger.error("Ratings : %s", e)
        dict_row["RYM Ratings"] = "NA"
        dict_row["Ratings"] = "NA"
        dict_row["Reviews"] = "NA"
    return dict_row


def get_artist_disco(
    browser, soup: BeautifulSoup, complementary_infos: bool
) -> List[dict]:
    """Returns a list of dicts containing infos about an artist discography."""

    # artist discography
    artist_disco = []
    artist = soup.find("h1", {"class": "artist_name_hdr"}).text.strip()
    logger.debug("Extracting discography for %s", artist)
    disco = soup.find("div", {"id": "discography"})
    logger.debug("Sections find_all")
    sections = disco.find_all("div", {"class": "disco_header_top"})
    for section in sections:
        category = section.find("h3").text.strip()
        logger.debug("Section %s", category)
        discs = section.find_next_sibling(
            "div", {"id": re.compile("disco_type_*")}
        ).find_all("div", {"class": "disco_release"})
        for disc in tqdm(discs, dynamic_ncols=True):
            album = disc.find("a", {"class", "album"})
            url_disc = "https://rateyourmusic.com" + album["href"]
            date = disc.find("span", {"class": re.compile("disco_year_*")})
            logger.debug(
                "Getting information for disc %s - %s - %s",
                artist,
                album.text.strip(),
                date.text.strip(),
            )
            dict_disc = {
                "Artist": artist,
                "Category": category,
                "Name": album.text.strip(),
                "URL": url_disc,
                "Date": date["title"].strip(),
                "Year": date.text.strip(),
                "Average Rating": disc.find("div", {"class": "disco_avg_rating"}).text,
                "Ratings": disc.find("div", {"class": "disco_ratings"}).text.replace(
                    ",", ""
                ),
                "Reviews": disc.find("div", {"class": "disco_reviews"}).text.replace(
                    ",", ""
                ),
            }
            if complementary_infos:
                dict_disc = get_complementary_infos_disc(browser, dict_disc, url_disc)
            artist_disco.append(dict_disc)
    return artist_disco


def get_complementary_infos_disc(browser, dict_disc: dict, url_disc: str) -> dict:
    """Returns a dict containing complementary informations for a disc."""
    try:
        browser.get_url(url_disc)
        soup = browser.get_soup()
        dict_complementary = {}
        table = soup.find("table", {"class": "album_info"})
        table_descriptors = [x.find("th").text.strip() for x in table.find_all("tr")]
        table_values = [
            " ".join(x.find("td").text.strip().replace("\n", ", ").split())
            for x in table.find_all("tr")
        ]
        for d, v in zip(table_descriptors, table_values):
            dict_complementary[d] = v

        try:
            dict_complementary["Rank Overall"] = [
                x.replace("#", "").replace(",", "")
                for y in dict_complementary["Ranked"].split(", ")
                if "overall" in y
                for x in y.split()
            ][0]
        except Exception as e:
            logger.debug("No overall rank found : %s", e)
        try:
            dict_complementary["Rank Year"] = [
                x.replace("#", "").replace(",", "")
                for y in dict_complementary["Ranked"].split(", ")
                if dict_disc["Year"] in y
                for x in y.split()
            ][0]
        except Exception as e:
            logger.debug("No year rank found : %s", e)
        dict_disc.update(dict_complementary)
    except Exception as e:
        logger.error(e)
    return dict_disc
