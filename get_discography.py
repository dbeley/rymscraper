import logging
import time
import argparse
import re
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

logger = logging.getLogger()
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
temps_debut = time.time()

options = Options()
options.headless = True
browser = webdriver.Firefox(options=options)


def get_soup(browser, url):
    logger.debug('get_soup(browser, %s)', url)
    # if cookie bar found, click on the ok button
    try:
        browser.find_element_by_class_name('as-oil__btn-optin').click()
        logger.debug("Cookie bar found. Clicking on ok.")
        # time.sleep(random.uniform(1, 2))
    except Exception as e:
        logger.debug("Cookie bar not found, %s", str(e).strip())

    logger.debug("browser.get(%s)", url)
    browser.get(str(url))

    soup = BeautifulSoup(browser.page_source, 'lxml')
    with open(f"Exports/last_soup.html", 'w') as f:
        f.write(soup.prettify())
    try:
        # rate-limit
        if soup.find('form', {'id': 'sec_verify'}):
            logger.error("Rate-limit detected. Restarting browser at %s", url)
            # with open(f"{export_directory}/ratelimit_detected.html", 'w') as f:
            #     f.write(soup.prettify())
            browser.quit()
            browser = webdriver.Firefox(options=options)
            soup.decompose()
            soup = get_soup(browser, url)

    except Exception as e:
        logger.error("Error scraping page %s : %s", url, e)
        exit()
        # with open(f"{export_directory}/soup_error.html", 'w') as f:
        #     f.write(soup.prettify())
        # break
    return soup


def get_urls_from_artists_name(browser, list_artists):
    list_urls = []
    base_url = "https://rateyourmusic.com"
    for index, artist in enumerate(list_artists, 1):
        artist = artist.replace(' ', '+')
        url = f"{base_url}/search?searchtype=a&searchterm={artist}"
        logger.debug("Searching %s in url %s", artist, url)
        soup = get_soup(browser, url)
        url_artist = f"{base_url}{soup.find('a', {'class': 'searchpage'})['href']}"
        logger.info("%s found : %s", artist, url_artist)
        list_urls.append(url_artist)
    return(list_urls)


def get_artist_disco(soup):
    artist_disco = []
    artist = soup.find('h1', {'class': 'artist_name_hdr'}).text.strip()
    logger.debug('Extracting discography for %s', artist)
    disco = soup.find('div', {'id': 'discography'})
    sections = disco.find_all('div', {'class': 'disco_header_top'})
    for section in sections:
        category = section.find('h3').text.strip()
        discs = section.find_next_sibling('div', {'id': re.compile('disco_type_*')}).find_all('div', {'class': 'disco_release'})
        for disc in discs:
            dict_disc = {}
            dict_disc['Artist'] = artist
            dict_disc['Category'] = category
            album = disc.find('a', {'class', 'album'})
            dict_disc['Name'] = album.text.strip()
            dict_disc['URL'] = "https://rateyourmusic.com" + album['href']
            date = disc.find('span', {'class': re.compile('disco_year_*')})
            dict_disc['Date'] = date['title'].strip()
            dict_disc['Year'] = date.text.strip()
            dict_disc['Average Rating'] = disc.find('div', {'class': 'disco_avg_rating'}).text
            dict_disc['Ratings'] = disc.find('div', {'class': 'disco_ratings'}).text
            dict_disc['Reviews'] = disc.find('div', {'class': 'disco_reviews'}).text
            # logger.debug('Final dict for %s : %s', artist, dict_disc)

            logger.debug('Getting information for disc %s - %s - %s', artist, album.text.strip(), date.text.strip())
            try:
                dict_disc_complementary = get_complementary_disc_infos(disc, dict_disc['URL'], dict_disc['Year'])
                # logger.debug('Complementary dict extracted : %s', dict_disc_complementary)
                dict_disc.update(dict_disc_complementary)
            except Exception as e:
                logger.error(e)
            artist_disco.append(dict_disc)

    return artist_disco


def get_complementary_disc_infos(disc, url, year):
    global browser

    soup = get_soup(browser, url)
    dict_complementary = {}
    table = soup.find('table', {'class': 'album_info'})
    table_descriptors = [x.find('th').text.strip() for x in table.find_all('tr')]
    table_values = [' '.join(x.find('td').text.strip().replace('\n', ', ').split()) for x in table.find_all('tr')]
    for d, v in zip(table_descriptors, table_values):
        dict_complementary[d] = v

    try:
        dict_complementary['Rank Overall'] = [x.replace('#', '') for y in dict_complementary['Ranked'].split(',') if 'overall' in y for x in y.split()][0]
    except Exception as e:
        logger.warning(e)
    try:
        dict_complementary['Rank Year'] = [x.replace('#', '') for y in dict_complementary['Ranked'].split(',') if year in y for x in y.split()][0]
    except Exception as e:
        logger.warning(e)
    return dict_complementary


def main():
    global browser
    args = parse_args()
    url = args.url
    artist = args.artist
    file_url = args.file_url
    file_artist = args.file_artist
    separate_export = args.separate_export

    if not any([url, artist, file_url, file_artist]):
        logger.error("Not enought arguments. Use -h to see available arguments.")
        exit()
    if url:
        list_urls = [x.strip() for x in url.split(',') if x.strip()]
        logger.debug("Option url found, list_urls : %s", list_urls)
    if file_url:
        try:
            with open(file_url) as f:
                list_urls = [x.strip() for x in f.readlines() if x.strip()]
        except Exception as e:
            logger.error(e)
            exit()
        logger.debug("Option file_url found, list_urls : %s", list_urls)
    if artist:
        list_artists = [x.strip() for x in artist.split(',') if x.strip()]
        logger.debug("Option artist found, list_artists : %s", list_artists)
    if file_artist:
        try:
            with open(file_artist) as f:
                list_artists = [x.strip() for x in f if x.strip()]
        except Exception as e:
            logger.error(e)
            exit()
        logger.debug("Option file_artist found, list_artists : %s", list_artists)

    if list_artists:
        list_urls = get_urls_from_artists_name(browser, list_artists)

    logger.debug('final list_urls : %s', list_urls)
    # exit()
    export_directory = "Exports"
    Path(export_directory).mkdir(parents=True, exist_ok=True)

    export_filename = f"{export_directory}/export_discography_{int(time.time())}"

    list_artists_disco = []
    for url in list_urls:
        logger.debug('Getting artist discography for url %s', url)

        soup = get_soup(browser, url)

        artist_disco = get_artist_disco(soup)
        list_artists_disco.extend(artist_disco)

        if separate_export:
            # have to put the dict in a list for some reason
            df_artist = pd.DataFrame([artist_disco], index=[0])
            export_filename_artist = f"{export_filename}_{artist_disco[0]['Name'].replace(' ', '_')}"
            df_artist.to_csv(export_filename_artist, sep='\t', index=False)

    browser.quit()

    columns = ['Artist',
               'Name',
               'URL',
               'Category',
               'Type',
               'Year',
               'Date',
               'Average Rating',
               'Ratings',
               'Reviews',
               'Genres',
               'Language',
               'Descriptors',
               'Recorded',
               ]

    df = pd.DataFrame(list_artists_disco)
    df = df[columns]
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
