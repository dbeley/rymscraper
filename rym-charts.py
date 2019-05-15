import logging
import time
import argparse
import random
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

logger = logging.getLogger()
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
temps_debut = time.time()


def get_soup(browser, url):
    delay = random.uniform(5, 20)
    logger.debug(f"Sleeping {round(delay, 2)} seconds before loading the page")
    time.sleep(delay)

    # if cookie bar found, click on the ok button
    try:
        browser.find_element_by_class_name('as-oil__btn-optin').click()
        logger.debug("Cookie bar found. Clicking on ok.")
        time.sleep(random.uniform(2, 4))
    except Exception as e:
        logger.debug(f"Cookie bar not found, {e}")

    logger.debug(f"browser.get({url})")
    browser.get(url)

    delay = random.uniform(1, 4)
    logger.debug(f"Sleeping {round(delay, 2)} seconds waiting for the page to load")
    time.sleep(delay)

    soup = BeautifulSoup(browser.page_source, 'lxml')
    return soup


def get_soup_next(browser, url):
    delay = random.uniform(5, 20)
    logger.debug(f"Sleeping {round(delay, 2)} seconds before clicking the link")
    time.sleep(delay)

    # if cookie bar found, click on the ok button
    try:
        browser.find_element_by_class_name('as-oil__btn-optin').click()
        logger.debug("Cookie bar found. Clicking on ok.")
        time.sleep(random.uniform(2, 4))
    except Exception as e:
        logger.debug(f"Cookie bar not found, {e}")

    logger.debug("Clicking on the next button")
    browser.find_element_by_class_name('navlinknext').click()

    delay = random.uniform(1, 4)
    logger.debug(f"Sleeping {round(delay, 2)} seconds waiting for the page to load")
    time.sleep(delay)
    soup = BeautifulSoup(browser.page_source, 'lxml')
    return soup


def get_row_infos(row):
    dict_row = {}
    try:
        dict_row['Rank'] = row.find('span', {'class': 'ooookiig'}).text
    except Exception as e:
        logger.error(f"Rank : {e}")
        dict_row['Rank'] = 'NA'
    try:
        dict_row['Artist'] = row.find('a', {'class': 'artist'}).text
    except Exception as e:
        logger.error(f"Artist: {e}")
        dict_row['Artist'] = 'NA'
    try:
        dict_row['Album'] = row.find('a', {'class': 'album'}).text
        logger.debug(f"{dict_row['Rank']} - {dict_row['Artist']} - {dict_row['Album']}")
    except Exception as e:
        logger.error(f"Album : {e}")
        dict_row['Album'] = 'NA'
    try:
        dict_row['Year'] = row.find('div', {'class': 'chart_year'}).text.replace('(', '').replace(')', '')
    except Exception as e:
        logger.error(f"Year : {e}")
        dict_row['Year'] = 'NA'
    try:
        dict_row['Genres'] = ', '.join([x.text for x in row.find('div', {'class': 'chart_detail_line3'}).find_all('a', {'class': 'genre'})])
    except Exception as e:
        logger.error(f"Genres : {e}")
        dict_row['Genres'] = 'NA'
    try:
        dict_row['Descriptors'] = row.find('div', {'class': 'extra_metadata_descriptors'}).text.strip()
    except Exception as e:
        logger.error(f"Descriptors : {e}")
        dict_row['Descriptors'] = 'NA'
    try:
        ratings = [x.strip() for x in row.find('div', {'class': 'chart_stats'}).find('a').text.split('|')]
        dict_row['RYM Rating'] = ratings[0].replace('RYM Rating: ', '')
        dict_row['Ratings'] = ratings[1].replace('Ratings: ', '')
        dict_row['Reviews'] = ratings[2].replace('Reviews: ', '')
    except Exception as e:
        logger.error(f"Ratings : {e}")
        dict_row['RYM Ratings'] = 'NA'
        dict_row['Ratings'] = 'NA'
        dict_row['Reviews'] = 'NA'
    return dict_row


def main():
    args = parse_args()
    url = args.url
    genre = args.genre
    year = args.year
    country = args.country
    everything = args.everything
    export_directory = "Exports"
    Path(export_directory).mkdir(parents=True, exist_ok=True)

    if not url:
        # Default url : top albums of all-time
        url = f"https://rateyourmusic.com/customchart?chart_type=top"
        export_filename = f"{export_directory}/export_chart"

        if everything:
            export_filename += f"_everything"
            url += f"&type=everything"
        else:
            export_filename += f"_album"
            url += f"&type=album"
        if year:
            export_filename += f"_{year}"
            url += f"&year={year}"
        if genre:
            export_filename += f"_{genre}"
            url += f"&genre_include=1&include_child_genres=1&genres={genre}"
        if country:
            export_filename += f"_{country}"
            url += f"&origin_countries={country}&limit=none"

    logger.debug(f"URL : {url}")

    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)
    # browser = webdriver.Firefox()

    page = 1
    soup = get_soup(browser, url + f"&page={page}")
    list_rows = []
    while True:
        try:
            if soup.select('table', {'class': 'mbgen'}):
                logger.debug("Table class mbgen found")
                table = soup.find('table', {'class': 'mbgen'})
                rows = table.find_all('tr')
                if len(rows) == 0:
                    logger.debug("No rows extracted. Exiting")
                    break
                for row in rows:
                    # don't parse ads
                    if not row.select('script'):
                        dict_row = get_row_infos(row)
                        list_rows.append(dict_row)
            else:
                logger.warning("Table class mbgen not found")
                logger.debug("Writing soup for debugging to mbgen_not_found.txt")
                with open(f"{export_directory}/mbgen_not_found.txt", 'w') as f:
                    f.write(soup.prettify())
                break
                # if page > 3:
                #     break
            if soup.select('a', {'class': 'navlinknext'}):
                logger.debug("Next page found")
                page += 1
                soup.decompose()
                # soup = get_soup_next(browser, url)
                soup = get_soup(browser, url + f"&page={page}")
            else:
                logger.debug("No next page found. Exiting.")
                break
        except Exception as e:
            logger.error(f"ERROR scraping page {url} : {e}")
            logger.debug("Writing soup for debugging to soup_error.txt")
            with open(f"{export_directory}/soup_error.txt", 'w') as f:
                f.write(soup.prettify())
            break

    browser.quit()

    columns = ['Rank',
               'Album',
               'Artist',
               'Genres',
               'Descriptors',
               'Year',
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
    parser.set_defaults(everything=False)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
