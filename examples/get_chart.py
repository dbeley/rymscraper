import logging
import time
import argparse
import pandas as pd
from pathlib import Path
import rymscraper
from rymscraper import RymUrl

logger = logging.getLogger()
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
temps_debut = time.time()


def main():
    args = parse_args()
    export_directory = "Exports"
    Path(export_directory).mkdir(parents=True, exist_ok=True)

    if not args.url:
        url = RymUrl.RymUrl()
        export_filename = f"{export_directory}/export_chart"
        logger.debug("rym_url : %s.", url)

        if args.everything:
            export_filename += f"_everything"
            url.url_part_type += f"everything"
        else:
            export_filename += f"_album"
            url.url_part_type += f"album"
        if args.year:
            export_filename += f"_{args.year}"
            url.url_part_year += f"{args.year}"
        if args.genre:
            export_filename += f"_{args.genre}"
            url.url_part_genres += f"{args.genre}"
        if args.country:
            export_filename += f"_{args.country}"
            url.url_part_origin_countries += f"{args.country}"
    else:
        url.url_page_separator = "/"
        export_filename = f"{export_directory}/export_url"

    logger.debug("completed rym_url : %s.", url)

    RymNetwork = rymscraper.RymNetwork(headless=args.no_headless)

    logger.info("Extracting infos from the chart.")
    list_rows = RymNetwork.get_chart_infos(url, max_page=args.page)

    columns = [
        "Rank",
        "Artist",
        "Album",
        "Date",
        "Genres",
        "RYM Rating",
        "Ratings",
        "Reviews",
    ]

    df = pd.DataFrame(list_rows)
    df = df[columns]
    logger.info("Exporting results to %s.", export_filename + ".csv")
    df.to_csv(export_filename + ".csv", sep="\t", index=False)

    RymNetwork.browser.close()
    RymNetwork.browser.quit()

    logger.debug("Runtime : %.2f seconds." % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scraper rateyourmusic (chart version)."
    )
    parser.add_argument(
        "--debug",
        help="Display debugging information.",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument("-u", "--url", help="Chart URL to parse.", type=str)
    parser.add_argument(
        "-g",
        "--genre",
        help="Chart Option : Genre (use + if you need a space).",
        type=str,
    )
    parser.add_argument("-y", "--year", help="Chart Option : Year.", type=str)
    parser.add_argument(
        "-c", "--country", help="Chart Option : Country.", type=str
    )
    parser.add_argument(
        "-p",
        "--page",
        help="Number of page to extract. If not set, every pages will be extracted.",
        type=int,
    )
    parser.add_argument(
        "-e",
        "--everything",
        help="Chart Option : Extract Everything / All Releases (otherwise only albums).",
        action="store_true",
        dest="everything",
    )
    parser.add_argument(
        "--no_headless",
        help="Launch selenium in foreground (background by default).",
        action="store_false",
        dest="no_headless",
    )
    parser.set_defaults(everything=False, no_headless=True)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
