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
    logger.info(f"URL : {url}")

    # if cookie bar found, click on the ok button
    try:
        browser.find_element_by_class_name('as-oil__btn-optin').click()
        logger.debug("Cookie bar found. Clicking on ok.")
        # time.sleep(random.uniform(1, 2))
    except Exception as e:
        logger.debug(f"Cookie bar not found, {e}")

    logger.debug(f"browser.get({url})")
    browser.get(str(url))

    soup = BeautifulSoup(browser.page_source, 'lxml')
    return soup


def get_urls_from_artists_name(browser, list_artists):
    list_urls = []
    base_url = "https://rateyourmusic.com"
    for index, artist in enumerate(list_artists, 1):
        url = f"{base_url}/search?searchtype=a&searchterm={artist}"
        soup = get_soup(browser, url)
        list_urls.append(f"{base_url}{soup.find('a', {'class': 'searchpage'})['href']}")
    return(list_urls)


def get_artist_info(soup):
    artist_info = {}
    artist_info['Name'] = soup.find('h1', {'class': 'artist_name_hdr'}).text.strip()

    artist_info_descriptors = [x.text.strip() for x in soup.find('div', {'class': 'artist_info'}).find_all('div', {'class': 'info_hdr'})]
    artist_info_values = [x.nextSibling.text.strip() for x in soup.find('div', {'class': 'artist_info'}).find_all('div', {'class': 'info_hdr'})]
    for d, v, in zip(artist_info_descriptors, artist_info_values):
        artist_info[d] = v

    return artist_info

def main():
    args = parse_args()
    url = args.url
    artist = args.artist
    file_url = args.file_url
    file_artist = args.file_artist
    separate_export = args.separate_export

    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)

    if url:
        list_urls = [x.strip() for x in url.split(',')]
    if file_url:
        try:
            with open(file_url) as f:
                if list_urls:
                    list_urls += [x.strip() for x in f.readlines()]
                else:
                    list_urls = [x.strip() for x in f.readlines()]
        except Exception as e:
            logger.error(e)
            exit()
    if artist:
        list_artists = [x.strip() for x in artist.split(',')]
    if file_artist:
        try:
            with open(file_artist) as f:
                if list_artists:
                    list_artists += [x.strip() for x in f.readlines()]
                else:
                    list_artists = [x.strip() for x in f.readlines()]
        except Exception as e:
            logger.error(e)
            exit()

    if list_artists:
        list_urls = get_urls_from_artists_name(browser, list_artists)

    logger.debug(list_urls)
    # exit()
    export_directory = "Exports"
    Path(export_directory).mkdir(parents=True, exist_ok=True)

    export_filename = f"{export_directory}/export_artist_{int(time.time())}"

    list_artists_infos = []
    for url in list_urls:

        soup = get_soup(browser, url)

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

        except Exception as e:
            logger.error(f"Error scraping page {url} : {e}")
            # with open(f"{export_directory}/soup_error.html", 'w') as f:
            #     f.write(soup.prettify())
            break

        artist_info = get_artist_info(soup)
        list_artists_infos.append(artist_info)

        if separate_export:
            # have to put the dict in a list for some reason
            df_artist = pd.DataFrame([artist_info], index=[0])
            export_filename_artist = f"{export_filename}_{artist_info['Name'].replace(' ', '_')}"
            df_artist.to_csv(export_filename_artist, sep='\t', index=False)

    browser.quit()

    df = pd.DataFrame(list_artists_infos)
    df.to_csv(export_filename + '.csv', sep='\t', index=False)

    logger.debug("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Scraper rateyourmusic (artist version).')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('-u', '--url', help="URL to extract (separated by comma)", type=str)
    parser.add_argument('--file_url', help="File containing the URL to extract (one by line)", type=str)
    parser.add_argument('--file_artist', help="File containing the artist to extract (one by line)", type=str)
    parser.add_argument('-a', '--artist', help="Artist to extract (separated by comma)", type=str)
    parser.add_argument('-s', '--separate_export', help="Also export the artists in separate files", action="store_true", dest="separate_export")
    parser.set_defaults(separate_export=False)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
