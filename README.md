# rymscraper

![Build Status](https://github.com/dbeley/rymscraper/workflows/CI/badge.svg)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8601652424ab44698fd00f6a46a2140e)](https://www.codacy.com/app/dbeley/rymscraper?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dbeley/rymscraper&amp;utm_campaign=Badge_Grade)

`rymscraper` is an **unofficial** Python API to extract data from [rateyourmusic.com](https://rateyourmusic.com) (👍 consider [supporting them](https://rateyourmusic.com/subscribe)!).

> :warning: **An excessive usage of `rymscraper` can make your IP address banned by rateyourmusic for a few days.**



## Requirements

- beautifulsoup4
- lxml
- requests
- pandas
- selenium with geckodriver
- tqdm

## Installation

Classic installation

```
python setup.py install
```

Installation in a virtualenv with pipenv

```
pipenv install '-e .'
```

## Example

The data format used by the library is the python dict. It can be easily converted to CSV or JSON.

```python
>>> import pandas as pd
>>> from rymscraper import rymscraper, RymUrl

>>> network = rymscraper.RymNetwork()
```

### Artist

```python
>>> artist_infos = network.get_artist_infos(name="Daft Punk")
>>> # or network.get_artist_infos(url="https://rateyourmusic.com/artist/daft-punk")
>>> import json
>>> json.dumps(artist_infos, indent=, ensure_ascii=False)
```

```
{
    "Name": "Daft Punk",
    "Formed": "1993, Paris, Île-de-France, France",
    "Disbanded": "22 February 2021",
    "Members": "Thomas Bangalter (programming, synthesizer, keyboards, drum machine, guitar, bass, vocals, vocoder, talk box), Guy-Manuel de Homem-Christo (programming, synthesizer, keyboards, drums, drum machine, guitar)",
    "Related Artists": "Darlin'",
    "Notes": "See also: Discovered: A Collection of Daft Funk Samples",
    "Also Known As": "Draft Ponk",
    "Genres": "French House, Film Score, Disco, Electronic, Synthpop, Electroclash"
}
```

```python
>>> # you can easily convert all returned values to a pandas dataframe
>>> df = pd.DataFrame([artist_infos])
>>> df[['Name', 'Formed', 'Disbanded']]
```

```
     Name                              Formed         Disbanded
Daft Punk  1993, Paris, Île-de-France, France  22 February 2021
```

You can also extract several artists at once:

```python
# several artists
>>> list_artists_infos = network.get_artists_infos(names=["Air", "M83"])
>>> # or network.get_artists_infos(urls=["https://rateyourmusic.com/artist/air", "https://rateyourmusic.com/artist/m83"])
>>> df = pd.DataFrame(list_artists_infos)
```

### Album

```python
>>> # name field should use the format Artist - Album name (not ideal but it works for now)
>>> album_infos = network.get_album_infos(name="XTC - Black Sea")
>>> # or network.get_album_infos(url="https://rateyourmusic.com/release/album/xtc/black-sea/")
>>> df = pd.DataFrame([album_infos])
```

You can also extract several albums at once:

```python
# several albums
>>> list_album_infos = network.get_albums_infos(names=["Ride - Nowhere", "Electrelane - Axes"])
>>> # or network.get_albums_infos(urls=["https://rateyourmusic.com/release/album/ride/nowhere/", "https://rateyourmusic.com/release/album/electrelane/axes/"])
>>> df = pd.DataFrame(list_album_infos)
```

#### Album Timeline

Number of ratings per day:

```python
>>> album_timeline = network.get_album_timeline(url="https://rateyourmusic.com/release/album/feu-chatterton/palais-dargile/")
>>> df = pd.DataFrame(album_timeline)
>>> df["Date"] = df["Date"].apply(lambda x: datetime.datetime.strptime(x, "%d %b %Y"))
>>> df["Date"].groupby(df["Date"].dt.to_period("D")).count().plot(kind="bar")
```

![timeline_plot](https://github.com/dbeley/rymscraper/blob/master/docs/timeline.png?raw=true)

### Chart

```python
>>> # (slow for very long charts)
>>> rym_url = RymUrl.RymUrl() # default: top of all-time. See examples/get_chart.py source code for more options.
>>> chart_infos = network.get_chart_infos(url=rym_url, max_page=3)
>>> df = pd.DataFrame(chart_infos)
>>> df[['Rank', 'Artist', 'Album', 'RYM Rating', 'Ratings']]
```

```
Rank                         Artist                                              Album RYM Rating Ratings
   1                      Radiohead                                        OK Computer       4.23   67360
   2                     Pink Floyd                                 Wish You Were Here       4.29   46534
   3                   King Crimson                   In the Court of the Crimson King       4.30   42784
   4                      Radiohead                                              Kid A       4.21   55999
   5            My Bloody Valentine                                           Loveless       4.24   47394
   6                 Kendrick Lamar                                To Pimp a Butterfly       4.27   41040
   7                     Pink Floyd                          The Dark Side of the Moon       4.20   55535
   8                    The Beatles                                         Abbey Road       4.25   42739
   9  The Velvet Underground & Nico                      The Velvet Underground & Nico       4.24   44002
  10                    David Bowie  The Rise and Fall of Ziggy Stardust and the Sp...       4.26   37963
```

### Discography

```python
>>> discography_infos = network.get_discography_infos(name="Aufgang", complementary_infos=True)
>>> # or network.get_discography_infos(url="https://rateyourmusic.com/artist/aufgang")
>>> df = pd.DataFrame.from_records(discography_infos)
```

```python
>>> # don't forget to close and quit the browser (prevent memory leaks)
>>> network.browser.close()
>>> network.browser.quit()
```

## Example Scripts

Some scripts are included in the examples folder.

- get_artist_infos.py : extract informations about one or several artists by name or url in a csv file.
- get_chart.py : extract albums information appearing in a chart by name, year or url in a csv file.
- get_discography.py : extract the discography of one or several artists by name or url in a csv file.
- get_album_infos.py : extract informations about one or several albums by name or url in a csv file.
- get_album_timeline.py : extract the timeline of an album into a json file.

### Usage

```
python get_artist_infos.py -a "u2,xtc,brad mehldau"
python get_artist_infos.py --file_artist artist_list.txt

python get_chart.py -g rock
python get_chart.py -g ambient -y 2010s -c France --everything

python get_discography.py -a magma
python get_discography.py -a "the new pornographers, ween, stereolab" --complementary_infos --separate_export

python get_album_infos.py -a "ride - nowhere"
python get_album_infos.py --file_url urls_list.txt --no_headless

python get_album_timeline.py -a "ride - nowhere"
python get_album_timeline.py -u "https://rateyourmusic.com/release/album/feu-chatterton/palais-dargile/"
```

### Help

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
  --debug               Display debugging information.
  -u URL, --url URL     URLs of the artists to extract (separated by comma).
  --file_url FILE_URL   File containing the URLs to extract (one by line).
  --file_artist FILE_ARTIST
                        File containing the artists to extract (one by line).
  -a ARTIST, --artist ARTIST
                        Artists to extract (separated by comma).
  -s, --separate_export
                        Also export the artists in separate files.
  --no_headless         Launch selenium in foreground (background by default).
```

```
python get_chart.py -h
```

```
usage: get_chart.py [-h] [--debug] [-u URL] [-g GENRE] [-y YEAR] [-c COUNTRY]
                    [-p PAGE] [-e] [--no_headless]

Scraper rateyourmusic (chart version).

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information.
  -u URL, --url URL     Chart URL to parse.
  -g GENRE, --genre GENRE
                        Chart Option : Genre (use + if you need a space).
  -y YEAR, --year YEAR  Chart Option : Year.
  -c COUNTRY, --country COUNTRY
                        Chart Option : Country.
  -p PAGE, --page PAGE  Number of page to extract. If not set, every pages
                        will be extracted.
  -e, --everything      Chart Option : Extract Everything / All Releases
                        (otherwise only albums).
  --no_headless         Launch selenium in foreground (background by default).
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
  --debug               Display debugging information.
  -u URL, --url URL     URLs to extract (separated by comma).
  --file_url FILE_URL   File containing the URLs to extract (one by line).
  --file_artist FILE_ARTIST
                        File containing the artists to extract (one by line).
  -a ARTIST, --artist ARTIST
                        Artists to extract (separated by comma).
  -s, --separate_export
                        Also export the artists in separate files.
  -c, --complementary_infos
                        Extract complementary informations for each releases
                        (slower, more requests on rym).
  --no_headless         Launch selenium in foreground (background by default).
```

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
  --debug               Display debugging information.
  -u URL, --url URL     URL to extract (separated by comma).
  --file_url FILE_URL   File containing the URLs to extract (one by line).
  --file_album_name FILE_ALBUM_NAME
                        File containing the name of the albums to extract (one
                        by line, format Artist - Album).
  -a ALBUM_NAME, --album_name ALBUM_NAME
                        Albums to extract (separated by comma, format Artist -
                        Album).
  -s, --separate_export
                        Also export the artists in separate files.
  --no_headless         Launch selenium in foreground (background by default).
```

```
python get_album_timeline.py -h
```

```
usage: get_album_timeline.py [-h] [--debug] [-u URL] [-a ALBUM_NAME]
                             [--no_headless]

Scraper rateyourmusic (album timeline version).

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information.
  -u URL, --url URL     URL to extract.
  -a ALBUM_NAME, --album_name ALBUM_NAME
                        Album to extract (format Artist - Album).
  --no_headless         Launch selenium in foreground (background by default).
```
