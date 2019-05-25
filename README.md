# rym-scraper

Scripts to scrap rateyourmusic.com

- get_album_infos.py : extract informations about one or several albums by name or url
- get_artist_infos.py : extract informations about one or several artists by name or url
- get_chart.py : extract albums information appearing in a chart by name, year or url
- get_discography.py : extract the discography of one or several artists by name or url

## Requirements

- bs4
- lxml
- requests
- pandas
- selenium
- tqdm

## Installation of the virtualenv (recommended)

```
pipenv install
```

## Usage

```
python get_album_infos.py -a "ride - nowhere"
python get_artist_infos.py -a "u2,xtc,brad mehldau"
python get_chart.py -g rock
python get_discography.py -a magma
```

## Help

```
python get_album_infos.py -h
```

```
usage: get_album_infos.py [-h] [--debug] [-u URL] [--file_url FILE_URL]
                          [--file_album_name FILE_ALBUM_NAME] [-a ALBUM_NAME]
                          [-s] [--no_headless]

Scraper rateyourmusic (album version).

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  -u URL, --url URL     URL to extract (separated by comma)
  --file_url FILE_URL   File containing the URL to extract (one by line)
  --file_album_name FILE_ALBUM_NAME
                        File containing the name of the albums to extract (one
                        by line, format Artist - Album)
  -a ALBUM_NAME, --album_name ALBUM_NAME
                        Album to extract (separated by comma, format Artist -
                        Album)
  -s, --separate_export
                        Also export the artists in separate files
  --no_headless         Launch selenium in foreground (background by default)
```

```
python get_artist_infos.py -h
```

```
usage: get_artist_infos.py [-h] [--debug] [-u URL] [--file_url FILE_URL]
                           [--file_artist FILE_ARTIST] [-a ARTIST] [-s]
                           [--no_headless]

Scraper rateyourmusic (artist version).

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  -u URL, --url URL     URL to extract (separated by comma)
  --file_url FILE_URL   File containing the URL to extract (one by line)
  --file_artist FILE_ARTIST
                        File containing the artist to extract (one by line)
  -a ARTIST, --artist ARTIST
                        Artist to extract (separated by comma)
  -s, --separate_export
                        Also export the artists in separate files
  --no_headless         Launch selenium in foreground (background by default)
```

```
python get_chart.py -h
```

```
usage: get_chart.py [-h] [--debug] [-u URL] [-g GENRE] [-y YEAR] [-c COUNTRY]
                    [-e] [--no_headless]

Scraper rateyourmusic (chart version).

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  -u URL, --url URL     Chart URL to parse
  -g GENRE, --genre GENRE
                        Genre (use + if you need a space)
  -y YEAR, --year YEAR  Year
  -c COUNTRY, --country COUNTRY
                        Country
  -e, --everything      Everything (otherwise only albums)
  --no_headless         Launch selenium in foreground (background by default)
```

```
python get_discography.py -h
```

```
usage: get_discography.py [-h] [--debug] [-u URL] [--file_url FILE_URL]
                          [--file_artist FILE_ARTIST] [-a ARTIST] [-s] [-c]
                          [--no_headless]

Scraper rateyourmusic (discography version).

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  -u URL, --url URL     URL to extract (separated by comma)
  --file_url FILE_URL   File containing the URL to extract (one by line)
  --file_artist FILE_ARTIST
                        File containing the artist to extract (one by line)
  -a ARTIST, --artist ARTIST
                        Artist to extract (separated by comma)
  -s, --separate_export
                        Also export the artists in separate files
  -c, --complementary_infos
                        Extract complementary_infos for each releases (slower,
                        more requests on rym)
  --no_headless         Launch selenium in foreground (background by default)
```
