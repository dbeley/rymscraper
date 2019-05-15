import logging
import time
import argparse
import random
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from rym_url import Rym_url

logger = logging.getLogger()
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
temps_debut = time.time()


def get_soup(browser, url):
    logger.info(f"URL : {url}")
    delay = random.uniform(1, 3)
    logger.debug(f"Sleeping {round(delay, 2)} seconds before loading the page")
    time.sleep(delay)

    # if cookie bar found, click on the ok button
    try:
        browser.find_element_by_class_name('as-oil__btn-optin').click()
        logger.debug("Cookie bar found. Clicking on ok.")
        time.sleep(random.uniform(1, 2))
    except Exception as e:
        logger.debug(f"Cookie bar not found, {e}")

    logger.debug(f"browser.get({url})")
    browser.get(str(url))

    delay = random.uniform(1, 2)
    logger.debug(f"Sleeping {round(delay, 2)} seconds waiting for the page to load")
    time.sleep(delay)

    soup = BeautifulSoup(browser.page_source, 'lxml')
    return soup


def get_soup_next(browser, url):
    logger.info(f"URL : {url}")
    delay = random.uniform(1, 3)
    logger.debug(f"Sleeping {round(delay, 2)} seconds before clicking the link")
    time.sleep(delay)

    # if cookie bar found, click on the ok button
    try:
        browser.find_element_by_class_name('as-oil__btn-optin').click()
        logger.debug("Cookie bar found. Clicking on ok.")
        time.sleep(random.uniform(1, 2))
    except Exception as e:
        logger.debug(f"Cookie bar not found, {e}")

    # trying to hide ad
    try:
        element = browser.find_element_by_xpath("//iframe[@class='tynt-ad-frame']")
        logger.debug("Ad detected, trying to hide it")
        browser.execute_script("arguments[0].style.visibility='hidden'", element)
    except Exception as e:
        logger.debug(f"No ad detected : {e}")
    try:
        element = browser.find_element_by_xpath("//iframe[@class='tynt-ad-frame-container']")
        logger.debug("Ad detected, trying to hide it")
        browser.execute_script("arguments[0].style.visibility='hidden'", element)
    except Exception as e:
        logger.debug(f"No ad detected : {e}")
    try:
        element = browser.find_element_by_xpath("//div[@class='tynt-ad-frame-container']")
        logger.debug("Ad detected, trying to hide it")
        browser.execute_script("arguments[0].style.visibility='hidden'", element)
    except Exception as e:
        logger.debug(f"No ad detected : {e}")
    try:
        element = browser.find_element_by_xpath("//div[@class='tynt-bottom-bar-pivot']")
        logger.debug("Ad detected, trying to hide it")
        browser.execute_script("arguments[0].style.visibility='hidden'", element)
    except Exception as e:
        logger.debug(f"No ad detected : {e}")
    try:
        element = browser.find_element_by_xpath("//div[@class='tynt-bottom-bar']")
        logger.debug("Ad detected, trying to hide it")
        browser.execute_script("arguments[0].style.visibility='hidden'", element)
    except Exception as e:
        logger.debug(f"No ad detected : {e}")

    logger.debug("Clicking on the next button")
    browser.find_element_by_class_name('navlinknext').click()

    delay = random.uniform(1, 2)
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
        dict_row['Ratings'] = ratings[1].replace('Ratings: ', '').replace(',', '')
        dict_row['Reviews'] = ratings[2].replace('Reviews: ', '').replace(',', '')
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
        url = Rym_url()
        export_filename = f"{export_directory}/export_chart"
        logger.debug(f"rym_url : {url}")

        if everything:
            export_filename += f"_everything"
            url.url_part_type += f"everything"
        else:
            export_filename += f"_album"
            url.url_part_type += f"album"
        if year:
            export_filename += f"_{year}"
            url.url_part_year += f"{year}"
        if genre:
            export_filename += f"_{genre}"
            url.url_part_genres += f"{genre}"
        if country:
            export_filename += f"_{country}"
            url.url_part_origin_countries += f"{country}"
    else:
        url.url_page_separator = "/"
        export_filename = f"{export_directory}/export_url"

    logger.debug(f"completed rym_url : {url}")

    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)

    soup = get_soup(browser, url)
    list_rows = []
    while True:
        try:
            # rate-limit
            if soup.find('form', {'id': 'sec_verify'}):
                logger.error(f"Rate-limit detected. Restarting browser at {url}")
                # with open(f"{export_directory}/ratelimit_detected.html", 'w') as f:
                #     f.write(soup.prettify())
                browser.quit()
                browser = webdriver.Firefox(options=options)
                soup.decompose()
                soup = get_soup(browser, url)

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
                    soup = get_soup(browser, url)
                except Exception as e:
                    logger.error(e)
                    break
            else:
                logger.debug("No next page found. Exiting.")
                break
        except Exception as e:
            logger.error(f"Error scraping page {url} : {e}")
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
    parser.set_defaults(everything=False)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
