import logging
import time
import argparse
import pandas as pd
from pathlib import Path
from rymscraper import rymscraper

logger = logging.getLogger()
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
temps_debut = time.time()


def main():
    args = parse_args()

    # arguments parsing
    if not any([args.url, args.artist, args.file_url, args.file_artist]):
        logger.error("Not enough arguments. Use -h to see available arguments.")
        exit()
    list_artists = None
    list_urls = None
    if args.url:
        list_urls = [x.strip() for x in args.url.split(",") if x.strip()]
        logger.debug("Option url found, list_urls : %s.", list_urls)
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
        logger.debug("Option file_url found, list_urls : %s.", list_urls)
    if args.artist:
        list_artists = [x.strip() for x in args.artist.split(",") if x.strip()]
        logger.debug("Option artist found, list_artists : %s.", list_artists)
    if args.file_artist:
        try:
            with open(args.file_artist) as f:
                list_artists = [
                    x.strip() for x in f if x.strip() and not x.startswith("#")
                ]
        except Exception as e:
            logger.error(e)
            exit()
        logger.debug("Option file_artist found, list_artists : %s.", list_artists)

    # # starting selenium browser
    RymNetwork = rymscraper.RymNetwork(headless=args.no_headless)
    logger.info("Extracting artist infos.")
    if list_artists:
        list_artists_disco = RymNetwork.get_discographies_infos(
            names=list_artists, complementary_infos=args.complementary_infos
        )
    elif list_urls:
        logger.debug(list_urls)
        list_artists_disco = RymNetwork.get_discographies_infos(
            urls=list_urls, complementary_infos=args.complementary_infos
        )

    RymNetwork.browser.close()
    RymNetwork.browser.quit()

    export_directory = "Exports"
    Path(export_directory).mkdir(parents=True, exist_ok=True)

    export_filename = f"{export_directory}/{int(time.time())}_export_discography"

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

    df = pd.DataFrame.from_records(list_artists_disco)
    # reorder columns
    # df = df[columns]
    logger.info("Exporting results to %s.", export_filename + ".csv")
    df.to_csv(export_filename + ".csv", sep="\t", index=False)

    logger.debug("Runtime : %.2f seconds." % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scraper rateyourmusic (discography version)."
    )
    parser.add_argument(
        "--debug",
        help="Display debugging information.",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "-u", "--url", help="URLs to extract (separated by comma).", type=str
    )
    parser.add_argument(
        "--file_url",
        help="File containing the URLs to extract (one by line).",
        type=str,
    )
    parser.add_argument(
        "--file_artist",
        help="File containing the artists to extract (one by line).",
        type=str,
    )
    parser.add_argument(
        "-a",
        "--artist",
        help="Artists to extract (separated by comma).",
        type=str,
    )
    parser.add_argument(
        "-s",
        "--separate_export",
        help="Also export the artists in separate files.",
        action="store_true",
        dest="separate_export",
    )
    parser.add_argument(
        "-c",
        "--complementary_infos",
        help="Extract complementary informations for each releases (slower, more requests on rym).",
        action="store_true",
        dest="complementary_infos",
    )
    parser.add_argument(
        "--no_headless",
        help="Launch selenium in foreground (background by default).",
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
