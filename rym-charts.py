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
    delay = random.uniform(1, 2)
    logger.debug(f"Sleeping {round(delay, 2)} seconds before loading the page")
    time.sleep(delay)
    logger.debug(f"browser.get({url})")
    browser.get(url)
    # logger.debug("Scrolling down")
    # time.sleep(1)
    # browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    delay = random.uniform(1, 4)
    logger.debug(f"Sleeping {round(delay, 2)} seconds waiting for the page to load")
    time.sleep(delay)
    soup = BeautifulSoup(browser.page_source, 'lxml')
    return soup


def get_soup_next(browser, url):
    delay = random.uniform(1, 10)
    logger.debug(f"Sleeping {round(delay, 2)} seconds before clicking the link")
    time.sleep(delay)
    logger.debug(f"browser.find_element().click()")
    browser.find_element_by_class_name('navlinknext').click()
    # logger.debug("Scrolling down")
    # time.sleep(1)
    # browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
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
    export_directory = "Exports"
    Path(export_directory).mkdir(parents=True, exist_ok=True)
    export_filename = f"{export_directory}/export_chart.csv"
    if genre:
        export_filename = f"{export_directory}/export_chart_{genre}.csv"
        url = f"https://rateyourmusic.com/customchart?page=1&genres={genre}"

    options = Options()
    options.headless = True
    # browser = webdriver.Firefox(options=options)
    browser = webdriver.Firefox()

    soup = get_soup(browser, url)
    # page = 0
    list_rows = []
    while True:
        try:
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
            # if page > 3:
            #     break
            if soup.select('a', {'class': 'navlinknext'}):
                logger.debug("Next page found")
                soup.decompose()
                soup = get_soup_next(browser, url)
                # url = f"https://rateyourmusic.com{soup.find('a', {'class': 'navlinknext'})['href']}"
                # page += 1
            else:
                logger.debug("No next page found. Exiting.")
                break
        except Exception as e:
            logger.error(f"ERROR scraping page {url} : {e}")
            logger.debug("Writing soup for debugging to soup_error.txt")
            with open("soup_error.txt", 'w') as f:
                f.write(soup.prettify())
            break

    browser.quit()

    columns = ['Rank',
               'Album',
               'Artist',
               'Genres',
               'Year',
               'RYM Rating',
               'Ratings',
               'Reviews'
               ]

    df = pd.DataFrame(list_rows)
    df = df[columns]
    df.to_csv(export_filename, sep='\t', index=False)

    logger.debug("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Scraper rateyourmusic (chart version).')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('-u', '--url', help="Chart URL to parse", type=str)
    parser.add_argument('-g', '--genre', help="Genre (use + if you need a space)", type=str)
    parser.set_defaults(test=False, international=False)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
