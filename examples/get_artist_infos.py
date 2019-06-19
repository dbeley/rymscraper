import logging
import time
import argparse
import pandas as pd
from pathlib import Path
import rymscraper

logger = logging.getLogger()
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
temps_debut = time.time()


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

    RymNetwork = rymscraper.RymNetwork(headless=args.no_headless)
    if list_artists:
        list_artists_infos = RymNetwork.get_artists_infos(names=list_artists)
    elif list_urls:
        logger.debug(list_urls)
        list_artists_infos = RymNetwork.get_artists_infos(urls=list_urls)

    # if list_artists:
    #     list_urls = get_urls_from_artist_name(browser, list_artists)

    # exit()
    export_directory = "Exports"
    Path(export_directory).mkdir(parents=True, exist_ok=True)

    export_filename = f"{export_directory}/export_artist_{int(time.time())}"

    RymNetwork.browser.quit()

    df = pd.DataFrame(list_artists_infos)
    df.to_csv(export_filename + ".csv", sep="\t", index=False)

    # list_artist_infos = []
    # for url in tqdm(list_urls, dynamic_ncols=True):
    #    browser.get_url(url)
    #    soup = browser.get_soup()

    #    artist_info = get_artist_info(soup)
    #    list_artist_infos.append(artist_info)

    #    if args.separate_export:
    #        # have to put the dict in a list for some reason
    #        df_artist = pd.DataFrame([artist_info], index=[0])
    #        export_filename_artist = (
    #            f"{export_filename}_{artist_info['Name'].replace(' ', '_')}"
    #        )
    #        df_artist.to_csv(export_filename_artist, sep="\t", index=False)

    # browser.quit()

    # df = pd.DataFrame(list_artist_infos)
    # df.to_csv(export_filename + ".csv", sep="\t", index=False)

    logger.debug("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scraper rateyourmusic (artist version)."
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
        "--no_headless",
        help="Launch selenium in foreground (background by default)",
        action="store_false",
        dest="no_headless",
    )
    parser.set_defaults(separate_export=False, no_headless=True)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
