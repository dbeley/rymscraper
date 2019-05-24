class Rym_url:
    def __init__(self):
        self.url_base = f"https://rateyourmusic.com/customchart?chart_type=top"
        self.url_part_type = "&type="
        self.url_part_year = "&year="
        self.url_part_genre_include = "&genre_include=1"
        self.url_part_child_genres = "&include_child_genres=1"
        self.url_part_genres = "&genres="
        self.url_part_include_child_genres_chk = "&include_child_genres_chk=1"
        self.url_part_include_both = "&include_both"
        self.url_part_origin_countries = "&origin_countries="
        self.url_part_limit = "&limit=none"
        self.url_part_countries = "&countries="
        self.page_separator = "&page="
        self.page = 1

    def __repr__(self):
        final_url = (
            self.url_base
            + self.url_part_type
            + self.url_part_year
            + self.url_part_genre_include
            + self.url_part_child_genres
            + self.url_part_genres
            + self.url_part_include_child_genres_chk
            + self.url_part_include_both
            + self.url_part_origin_countries
            + self.url_part_limit
            + self.url_part_countries
            + self.page_separator
            + str(self.page)
        )
        return final_url
