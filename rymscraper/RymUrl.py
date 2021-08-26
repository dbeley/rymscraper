# For now you will have to directly change the string values. Look at examples/get_chart.py for examples.
# https://rateyourmusic.com/charts/top/release/1984-2002/g:ambient/loc:france/minr:200/
# https://rateyourmusic.com/charts/top/album,ep,single,unauth,djmix/2010s/g:ambient,blues/d:atmosphere,form,theme,bittersweet,epic/s:classical%2dmusic/loc:algeria,bouvet%2disland%2dbouvetoya,europe,antarctica%2d1/minr:200/pop:5/
class RymUrl:
    def __init__(self):
        self.url_base = f"https://rateyourmusic.com/charts/top"
        self.url_part_type = "/album"
        self.url_part_year = ""
        self.url_part_genres = ""
        # self.url_part_include_child_genres_chk = "&include_child_genres_chk=1"
        # self.url_part_include_both = "&include_both"
        self.url_part_origin_countries = ""
        # self.url_part_limit = "&limit=none"
        # self.url_part_countries = "&countries="
        self.page_separator = "/"
        self.page = 1

    def __repr__(self):
        final_url = (
            self.url_base
            + self.url_part_type
            + self.url_part_year
            # + self.url_part_genre_include
            # + self.url_part_child_genres
            + self.url_part_genres
            # + self.url_part_include_child_genres_chk
            # + self.url_part_include_both
            + self.url_part_origin_countries
            # + self.url_part_limit
            # + self.url_part_countries
            + self.page_separator
            + str(self.page)
            + '/'
        )
        return final_url
