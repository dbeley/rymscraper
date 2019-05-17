import logging
import time
import argparse
import pandas as pd
from pathlib import Path
from utils.rym_url import Rym_url
from utils.rym_browser import Rym_browser

logger = logging.getLogger()
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
temps_debut = time.time()


def get_row_infos(row):
    dict_row = {}
    try:
        dict_row['Rank'] = row.find('span', {'class': 'ooookiig'}).text
    except Exception as e:
        logger.error("Rank : %s", e)
        dict_row['Rank'] = 'NA'
    try:
        dict_row['Artist'] = row.find('a', {'class': 'artist'}).text
    except Exception as e:
        logger.error("Artist: %s", e)
        dict_row['Artist'] = 'NA'
    try:
        dict_row['Album'] = row.find('a', {'class': 'album'}).text
        logger.debug("%s - %s - %s", dict_row['Rank'], dict_row['Artist'], dict_row['Album'])
    except Exception as e:
        logger.error("Album : %s", e)
        dict_row['Album'] = 'NA'
    try:
        dict_row['Year'] = row.find('div', {'class': 'chart_year'}).text.replace('(', '').replace(')', '')
    except Exception as e:
        logger.error("Year : %s", e)
        dict_row['Year'] = 'NA'
    try:
        dict_row['Genres'] = ', '.join([x.text for x in row.find('div', {'class': 'chart_detail_line3'}).find_all('a', {'class': 'genre'})])
    except Exception as e:
        logger.error("Genres : %s", e)
        dict_row['Genres'] = 'NA'
    try:
        ratings = [x.strip() for x in row.find('div', {'class': 'chart_stats'}).find('a').text.split('|')]
        dict_row['RYM Rating'] = ratings[0].replace('RYM Rating: ', '')
        dict_row['Ratings'] = ratings[1].replace('Ratings: ', '').replace(',', '')
        dict_row['Reviews'] = ratings[2].replace('Reviews: ', '').replace(',', '')
    except Exception as e:
        logger.error("Ratings : %s", e)
        dict_row['RYM Ratings'] = 'NA'
        dict_row['Ratings'] = 'NA'
        dict_row['Reviews'] = 'NA'
    return dict_row


def main():
    args = parse_args()
    export_directory = "Exports"
    Path(export_directory).mkdir(parents=True, exist_ok=True)

    if not args.url:
        url = Rym_url()
        export_filename = f"{export_directory}/export_chart"
        logger.debug("rym_url : %s", url)

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

    logger.debug("completed rym_url : %s", url)

    browser = Rym_browser(headless=args.no_headless)

    list_rows = []
    while True:
        try:
            browser.get_url(url)
            soup = browser.get_soup()

            # table containing albums
            if soup.find('table', {'class': 'mbgen'}):
                logger.debug("Table class mbgen found")
                table = soup.find('table', {'class': 'mbgen'})
                rows = table.find_all('tr')
                if len(rows) == 0:
                    logger.debug("No rows extracted. Exiting")
                    break
                for row in rows:
                    # don't parse ads
                    if not row.find('script'):
                        dict_row = get_row_infos(row)
                        list_rows.append(dict_row)
            else:
                logger.warning("Table class mbgen not found")
                # with open(f"{export_directory}/mbgen_not_found.html", 'w') as f:
                #     f.write(soup.prettify())
                break

            # link to the next page
            if soup.find('a', {'class': 'navlinknext'}):
                logger.debug("Next page found")
                url.page += 1
                soup.decompose()
                try:
                    browser.get_url(url)
                    soup = browser.get_soup()
                except Exception as e:
                    logger.error(e)
                    break
            else:
                logger.debug("No next page found. Exiting.")
                break
        except Exception as e:
            logger.error("Error scraping page %s : {e}", url)
            # with open(f"{export_directory}/soup_error.html", 'w') as f:
            #     f.write(soup.prettify())
            break

    browser.quit()

    columns = ['Rank',
               'Artist',
               'Album',
               'Year',
               'Genres',
               'RYM Rating',
               'Ratings',
               'Reviews'
               ]

    df = pd.DataFrame(list_rows)
    df = df[columns]
    df.to_csv(export_filename + '.csv', sep='\t', index=False)

    logger.debug("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Scraper rateyourmusic (chart version).')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('-u', '--url', help="Chart URL to parse", type=str)
    parser.add_argument('-g', '--genre', help="Genre (use + if you need a space)", type=str)
    parser.add_argument('-y', '--year', help="Year", type=str)
    parser.add_argument('-c', '--country', help="Country", type=str)
    parser.add_argument('-e', '--everything', help="Everything (otherwise only albums)", action="store_true", dest="everything")
    parser.add_argument('--no_headless', help="Launch selenium in foreground (background by default)", action="store_false", dest="no_headless")
    parser.set_defaults(everything=False, no_headless=True)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
