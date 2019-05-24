import logging
import time
import argparse
import re
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from utils.rym_browser import Rym_browser
from utils.rym_utils import get_urls_from_artist_name

logger = logging.getLogger()
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
temps_debut = time.time()


def get_artist_disco(browser, url, complementary_infos):
    browser.get_url(url)
    soup = browser.get_soup()

    # artist discography
    artist_disco = []
    artist = soup.find("h1", {"class": "artist_name_hdr"}).text.strip()
    logger.info("Extracting discography for %s", artist)
    disco = soup.find("div", {"id": "discography"})
    logger.debug("Sections find_all")
    sections = disco.find_all("div", {"class": "disco_header_top"})
    for section in sections:
        category = section.find("h3").text.strip()
        logger.info("Section %s", category)
        discs = section.find_next_sibling(
            "div", {"id": re.compile("disco_type_*")}
        ).find_all("div", {"class": "disco_release"})
        for disc in tqdm(discs, dynamic_ncols=True):
            dict_disc = {}
            dict_disc["Artist"] = artist
            dict_disc["Category"] = category
            album = disc.find("a", {"class", "album"})
            dict_disc["Name"] = album.text.strip()
            url_disc = "https://rateyourmusic.com" + album["href"]
            dict_disc["URL"] = url_disc
            date = disc.find("span", {"class": re.compile("disco_year_*")})
            dict_disc["Date"] = date["title"].strip()
            dict_disc["Year"] = date.text.strip()
            dict_disc["Average Rating"] = disc.find(
                "div", {"class": "disco_avg_rating"}
            ).text
            dict_disc["Ratings"] = disc.find(
                "div", {"class": "disco_ratings"}
            ).text.replace(",", "")
            dict_disc["Reviews"] = disc.find(
                "div", {"class": "disco_reviews"}
            ).text.replace(",", "")
            # logger.debug('Final dict for %s : %s', artist, dict_disc)

            logger.debug(
                "Getting information for disc %s - %s - %s",
                artist,
                album.text.strip(),
                date.text.strip(),
            )
            if complementary_infos:
                dict_disc = get_complementary_infos_disc(
                    browser, dict_disc, url_disc
                )
            artist_disco.append(dict_disc)
    return artist_disco


def get_complementary_infos_disc(browser, dict_disc, url_disc):
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
        # logger.debug('Complementary dict extracted : %s', dict_disc_complementary)
        dict_disc.update(dict_complementary)
    except Exception as e:
        logger.error(e)
    return dict_disc


def main():
    args = parse_args()

    # arguments parsing
    if not any([args.url, args.artist, args.file_url, args.file_artist]):
        logger.error(
            "Not enought arguments. Use -h to see available arguments."
        )
        exit()
    if args.url:
        list_urls = [x.strip() for x in args.url.split(",") if x.strip()]
        logger.debug("Option url found, list_urls : %s", list_urls)
    if args.file_url:
        try:
            with open(args.file_url) as f:
                list_urls = [
                    x.strip()
                    for x in f.readlines()
                    if x.strip() and not x.startswith("#")
                ]
        except Exception as e:
            logger.error(e)
            exit()
        logger.debug("Option file_url found, list_urls : %s", list_urls)
    if args.artist:
        list_artists = [x.strip() for x in args.artist.split(",") if x.strip()]
        logger.debug("Option artist found, list_artists : %s", list_artists)
    if args.file_artist:
        try:
            with open(args.file_artist) as f:
                list_artists = [
                    x.strip() for x in f if x.strip() and not x.startswith("#")
                ]
        except Exception as e:
            logger.error(e)
            exit()
        logger.debug(
            "Option file_artist found, list_artists : %s", list_artists
        )

    # starting selenium browser
    browser = Rym_browser(headless=args.no_headless)

    # search url from artist name
    if list_artists:
        list_urls = get_urls_from_artist_name(browser, list_artists)

    logger.debug("final list_urls : %s", list_urls)
    export_directory = "Exports"
    Path(export_directory).mkdir(parents=True, exist_ok=True)

    export_filename = (
        f"{export_directory}/export_discography_{int(time.time())}"
    )

    # extracting discography
    list_artist_disco = []
    for url in list_urls:
        logger.debug("Getting artist discography for url %s", url)

        artist_disco = get_artist_disco(browser, url, args.complementary_infos)
        list_artist_disco.extend(artist_disco)

        if args.separate_export:
            # have to put the dict in a list for some reason
            df_artist = pd.DataFrame([artist_disco], index=[0])
            export_filename_artist = f"{export_filename}_{artist_disco[0]['Name'].replace(' ', '_')}"
            df_artist.to_csv(export_filename_artist, sep="\t", index=False)

    browser.quit()

    # columns = ['Artist',
    #            'Name',
    #            'URL',
    #            'Category',
    #            'Type',
    #            'Year',
    #            'Date',
    #            'Average Rating',
    #            'Ratings',
    #            'Reviews',
    #            'Genres',
    #            'Language',
    #            'Descriptors',
    #            'Recorded',
    #            ]

    df = pd.DataFrame(list_artist_disco)
    # reorder columns
    # df = df[columns]
    df.to_csv(export_filename + ".csv", sep="\t", index=False)

    logger.debug("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scraper rateyourmusic (discography version)."
    )
    parser.add_argument(
        "--debug",
        help="Display debugging information",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "-u", "--url", help="URL to extract (separated by comma)", type=str
    )
    parser.add_argument(
        "--file_url",
        help="File containing the URL to extract (one by line)",
        type=str,
    )
    parser.add_argument(
        "--file_artist",
        help="File containing the artist to extract (one by line)",
        type=str,
    )
    parser.add_argument(
        "-a",
        "--artist",
        help="Artist to extract (separated by comma)",
        type=str,
    )
    parser.add_argument(
        "-s",
        "--separate_export",
        help="Also export the artists in separate files",
        action="store_true",
        dest="separate_export",
    )
    parser.add_argument(
        "-c",
        "--complementary_infos",
        help="Extract complementary_infos for each releases (slower, more requests on rym)",
        action="store_true",
        dest="complementary_infos",
    )
    parser.add_argument(
        "--no_headless",
        help="Launch selenium in foreground (background by default)",
        action="store_false",
        dest="no_headless",
    )
    parser.set_defaults(
        separate_export=False, no_headless=True, complementary_infos=False
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
