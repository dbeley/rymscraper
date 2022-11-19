# For now you will have to directly change the string values. Look at examples/get_chart.py for examples.
# https://rateyourmusic.com/charts/top/release/1984-2002/g:ambient/loc:france/minr:200/
# https://rateyourmusic.com/charts/top/album,ep,single,unauth,djmix/2010s/g:ambient,blues/d:atmosphere,form,theme,bittersweet,epic/s:classical%2dmusic/loc:algeria,bouvet%2disland%2dbouvetoya,europe,antarctica%2d1/minr:200/pop:5/
from typing import Optional


class RymUrl:
    @staticmethod
    def sanitize_name(name: Optional[str]) -> Optional[str]:
        if name is None:
            return None
        return name.replace(" ", "-")

    def __init__(self, kind="album", year="all-time", genres: str = None, origin_countries: str = None, language: str = None, descriptors: str = None, page=1):
        """The language should be the 2 letter code for the language. For example, English is en, French is fr, etc."""
        self.url_base = "https://rateyourmusic.com/charts/top"

        self.kind = kind
        self.year = year
        self.genres = self.sanitize_name(genres)
        self.origin_countries = self.sanitize_name(origin_countries)
        self.language = self.sanitize_name(language)
        self.descriptors = self.sanitize_name(descriptors)
        self.page = page

    def __repr__(self):
        genres = f"/g:{self.genres}" if self.genres else ""
        origin_countries = f"/loc:{self.origin_countries}" if self.origin_countries else ""
        language = f"/l:{self.language}" if self.language else ""
        descriptors = f"/d:{self.descriptors}" if self.descriptors else ""
        final_url = f"{self.url_base}/{self.kind}/{self.year}{genres}{origin_countries}{language}{descriptors}/{self.page}/"

        return final_url