#!/usr/bin/env python3
import logging
import time
import argparse
from pathlib import Path
from rymscraper import rymscraper
import json

logger = logging.getLogger()
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
temps_debut = time.time()


def main():
    args = parse_args()

    # arguments parsing
    if not any([args.url, args.album_name]):
        logger.error("Not enough arguments. Use -h to see available arguments.")
        exit()

    RymNetwork = rymscraper.RymNetwork(headless=args.no_headless)
    logger.info("Extracting album timeline.")
    if args.album_name:
        album_timeline = RymNetwork.get_album_timeline(name=args.album_name)
    elif args.url:
        album_timeline = RymNetwork.get_album_timeline(url=args.url)

    export_directory = "Exports"
    Path(export_directory).mkdir(parents=True, exist_ok=True)

    if args.album_name:
        export_name = args.album_name
    else:
        export_name = " - ".join(args.url.split("/")[-3:-1])

    export_filename = f"{export_directory}/{int(time.time())}_export_album_timeline_{export_name}.json"
    logger.info("Exporting results to %s.", export_filename)
    with open(export_filename, "w") as f:
        f.write(json.dumps(album_timeline, indent=4, ensure_ascii=False))

    RymNetwork.browser.close()
    RymNetwork.browser.quit()

    logger.debug("Runtime : %.2f seconds." % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scraper rateyourmusic (album timeline version)."
    )
    parser.add_argument(
        "--debug",
        help="Display debugging information.",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument("-u", "--url", help="URL to extract.", type=str)
    parser.add_argument(
        "-a",
        "--album_name",
        help="Album to extract (format Artist - Album).",
        type=str,
    )
    parser.add_argument(
        "--no_headless",
        help="Launch selenium in foreground (background by default).",
        action="store_false",
        dest="no_headless",
    )
    parser.set_defaults(no_headless=True)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
