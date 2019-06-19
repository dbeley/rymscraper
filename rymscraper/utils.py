import logging
import re
from tqdm import tqdm
import difflib

logger = logging.getLogger(__name__)


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
            difflib.get_close_matches(album_name, artist_album_name)[0]
        )
    ]
    logger.debug("Best match : %s", url_match)
    return url_match


def get_album_infos(soup):
    """Returns a dict containing infos from an album."""
    album_infos = {
        "Name": soup.find("div", {"class": "album_title"})
        .text.split("\n")[0]
        .strip(),
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

    return album_infos


def get_artist_infos(soup):
    """Returns a dict containing infos from an artist."""
    artist_infos = {
        "Name": soup.find("h1", {"class": "artist_name_hdr"}).text.strip()
    }

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
    ]
    for d, v in zip(artist_infos_descriptors, artist_infos_values):
        artist_infos[d] = v

    try:
        del artist_infos["Share"]
    except KeyError:
        pass

    return artist_infos


def get_chart_row_infos(row):
    """Returns a dict containing infos from a chart row."""
    dict_row = {}
    try:
        dict_row["Rank"] = row.find("span", {"class": "ooookiig"}).text
    except Exception as e:
        logger.error("Rank : %s", e)
        dict_row["Rank"] = "NA"
    try:
        dict_row["Artist"] = row.find("a", {"class": "artist"}).text
    except Exception as e:
        logger.error("Artist: %s", e)
        dict_row["Artist"] = "NA"
    try:
        dict_row["Album"] = row.find("a", {"class": "album"}).text
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
        dict_row["Year"] = (
            row.find("div", {"class": "chart_year"})
            .text.replace("(", "")
            .replace(")", "")
        )
    except Exception as e:
        logger.error("Year : %s", e)
        dict_row["Year"] = "NA"
    try:
        dict_row["Genres"] = ", ".join(
            [
                x.text
                for x in row.find(
                    "div", {"class": "chart_detail_line3"}
                ).find_all("a", {"class": "genre"})
            ]
        )
    except Exception as e:
        logger.error("Genres : %s", e)
        dict_row["Genres"] = "NA"
    try:
        ratings = [
            x.strip()
            for x in row.find("div", {"class": "chart_stats"})
            .find("a")
            .text.split("|")
        ]
        dict_row["RYM Rating"] = ratings[0].replace("RYM Rating: ", "")
        dict_row["Ratings"] = (
            ratings[1].replace("Ratings: ", "").replace(",", "")
        )
        dict_row["Reviews"] = (
            ratings[2].replace("Reviews: ", "").replace(",", "")
        )
    except Exception as e:
        logger.error("Ratings : %s", e)
        dict_row["RYM Ratings"] = "NA"
        dict_row["Ratings"] = "NA"
        dict_row["Reviews"] = "NA"
    return dict_row


def get_artist_disco(browser, url, complementary_infos):
    """Returns a list of dicts containing infos about an artist discography."""
    browser.get_url(url)
    soup = browser.get_soup()

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
                "Average Rating": disc.find(
                    "div", {"class": "disco_avg_rating"}
                ).text,
                "Ratings": disc.find(
                    "div", {"class": "disco_ratings"}
                ).text.replace(",", ""),
                "Reviews": disc.find(
                    "div", {"class": "disco_reviews"}
                ).text.replace(",", ""),
            }
            if complementary_infos:
                dict_disc = get_complementary_infos_disc(
                    browser, dict_disc, url_disc
                )
            artist_disco.append(dict_disc)
    return artist_disco


def get_complementary_infos_disc(browser, dict_disc, url_disc):
    """Returns a dict containing complementary informations for a disc."""
    try:
        # complementary infos
        browser.get_url(url_disc)
        soup = browser.get_soup()
        dict_complementary = {}
        table = soup.find("table", {"class": "album_info"})
        table_descriptors = [
            x.find("th").text.strip() for x in table.find_all("tr")
        ]
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
