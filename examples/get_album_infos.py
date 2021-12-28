#!/usr/bin/env python3
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
    if not any([args.url, args.album_name, args.file_url, args.file_album_name]):
        logger.error("Not enough arguments. Use -h to see available arguments.")
        exit()
    list_urls = None
    list_albums = None
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
    if args.album_name:
        list_albums = [x.strip() for x in args.album_name.split(",") if x.strip()]
        logger.debug("Option album_name found, list_albums : %s.", list_albums)
    if args.file_album_name:
        try:
            with open(args.file_album_name) as f:
                list_albums = [
                    x.strip() for x in f if not x.startswith("#") and x.strip()
                ]
        except Exception as e:
            logger.error(e)
            exit()
        logger.debug("Option file_album_name found, list_albums : %s.", list_albums)

    RymNetwork = rymscraper.RymNetwork(headless=args.no_headless)
    logger.info("Extracting albums infos.")
    if list_albums:
        list_albums_infos = RymNetwork.get_albums_infos(names=list_albums)
    elif list_urls:
        logger.debug(list_urls)
        list_albums_infos = RymNetwork.get_albums_infos(urls=list_urls)

    export_directory = "Exports"
    Path(export_directory).mkdir(parents=True, exist_ok=True)

    export_filename = f"{export_directory}/{int(time.time())}_export_album"

    RymNetwork.browser.close()
    RymNetwork.browser.quit()

    logger.info("Exporting results to %s.", export_filename + ".csv")
    df = pd.DataFrame(list_albums_infos)
    df.to_csv(export_filename + ".csv", sep="\t", index=False)

    logger.debug("Runtime : %.2f seconds." % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scraper rateyourmusic (album version)."
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
        "-u", "--url", help="URL to extract (separated by comma).", type=str
    )
    parser.add_argument(
        "--file_url",
        help="File containing the URLs to extract (one by line).",
        type=str,
    )
    parser.add_argument(
        "--file_album_name",
        help="File containing the name of the albums to extract (one by line, format Artist - Album).",
        type=str,
    )
    parser.add_argument(
        "-a",
        "--album_name",
        help="Albums to extract (separated by comma, format Artist - Album).",
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
        "--no_headless",
        help="Launch selenium in foreground (background by default).",
        action="store_false",
        dest="no_headless",
    )
    parser.set_defaults(separate_export=False, no_headless=True)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
