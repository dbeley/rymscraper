import logging
import time
import argparse
import requests
from bs4 import BeautifulSoup


logger = logging.getLogger()
temps_debut = time.time()


def get_soup(url):
    return BeautifulSoup(requests.get(url).content, 'lxml')


def main():
    args = parse_args()
    url = args.url

    soup = get_soup(url)
    album = {}
    artists = [x for x in soup.find_all('a', {'class': 'artist'})]

    print(artists)
    

    logger.debug("Runtime : %.2f seconds" % (time.time() - temps_debut))

def parse_args():
    parser = argparse.ArgumentParser(description='Scraper rateyourmusic (chart version).')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('-u', '--url', help="Chart URL to parse", type=str)
    parser.set_defaults(test=False, international=False)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args

if __name__ == '__main__':
    main()
