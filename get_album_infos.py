import logging
import time
import argparse
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from utils.rym_browser import Rym_browser
from utils.rym_utils import get_urls_from_album_name

logger = logging.getLogger()
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
temps_debut = time.time()


def get_album_info(soup):
    album_info = {}
    album_info['Name'] = soup.find('div', {'class': 'album_title'}).text.split('\n')[0].strip()
    album_info['Artist'] = soup.find('div', {'class': 'album_title'}).text.split('\n')[2].strip()[3:]

    album_infos = [[x.find('th').text.strip(), x.find('td').text.strip()] for x in soup.find('table', {'class': 'album_info'}).find_all('tr')]
    # album_info_descriptors = [x.text.strip() for x in soup.find('table', {'class': 'album_info'}).find_all('th', {'class': 'info_hdr'})]
    # album_info_values = [x.nextSibling.text.strip() for x in soup.find('table', {'class': 'album_info'}).find_all('div', {'class': 'info_hdr'})]
    # for d, v, in zip(album_info_descriptors, album_info_values):
    for info in album_infos:
        album_info[info[0]] = info[1]

    return album_info


def main():
    args = parse_args()

    # arguments parsing
    if not any([args.url, args.album_name, args.file_url, args.file_album_name]):
        logger.error("Not enought arguments. Use -h to see available arguments.")
        exit()
    if args.url:
        list_urls = [x.strip() for x in args.url.split(',') if x.strip()]
        logger.debug("Option url found, list_urls : %s", list_urls)
    if args.file_url:
        try:
            with open(args.file_url) as f:
                list_urls = [x.strip() for x in f.readlines() if x.strip() and not x.startswith('#')]
        except Exception as e:
            logger.error(e)
            exit()
        logger.debug("Option file_url found, list_urls : %s", list_urls)
    if args.album_name:
        list_albums = [[x.strip() for x in y.split('-')] for y in args.album_name.split(',') if y.strip()]
        logger.debug("Option album_name found, list_albums : %s", list_albums)
    if args.file_album_name:
        try:
            with open(args.file_album_name) as f:
                list_albums = [[x.strip() for x in y.split('-')] for y in f if y.strip() and not y.startswith('#')]
        except Exception as e:
            logger.error(e)
            exit()
        logger.debug("Option file_album_name found, list_albums : %s", list_albums)

    # starting selenium browser
    browser = Rym_browser(headless=args.no_headless)

    if list_albums:
        list_urls = get_urls_from_album_name(browser, list_albums)

    logger.debug(list_urls)
    # exit()
    export_directory = "Exports"
    Path(export_directory).mkdir(parents=True, exist_ok=True)

    export_filename = f"{export_directory}/export_album_{int(time.time())}"

    list_album_infos = []
    for url in tqdm(list_urls, dynamic_ncols=True):
        browser.get_url(url)
        soup = browser.get_soup()

        album_info = get_album_info(soup)
        list_album_infos.append(album_info)

        if args.separate_export:
            # have to put the dict in a list for some reason
            df_album = pd.DataFrame([album_info], index=[0])
            export_filename_album = f"{export_filename}_{album_info['Name'].replace(' ', '_')}"
            df_album.to_csv(export_filename_album, sep='\t', index=False)

    browser.quit()

    df = pd.DataFrame(list_album_infos)
    df.to_csv(export_filename + '.csv', sep='\t', index=False)

    logger.debug("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Scraper rateyourmusic (album version).')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('-u', '--url', help="URL to extract (separated by comma)", type=str)
    parser.add_argument('--file_url', help="File containing the URL to extract (one by line)", type=str)
    parser.add_argument('--file_album_name', help="File containing the name of the albums to extract (one by line, format Artist - Album)", type=str)
    parser.add_argument('-a', '--album_name', help="Album to extract (separated by comma, format Artist - Album)", type=str)
    parser.add_argument('-s', '--separate_export', help="Also export the artists in separate files", action="store_true", dest="separate_export")
    parser.add_argument('--no_headless', help="Launch selenium in foreground (background by default)", action="store_false", dest="no_headless")
    parser.set_defaults(separate_export=False, no_headless=True)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
