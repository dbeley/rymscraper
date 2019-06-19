from rymscraper import RymUrl


def test_RymUrlSimple():
    RymUrlTest = RymUrl.RymUrl()
    if (
        str(RymUrlTest)
        != "https://rateyourmusic.com/customchart?chart_type=top&type=&year=&genre_include=1&include_child_genres=1&genres=&include_child_genres_chk=1&include_both&origin_countries=&limit=none&countries=&page=1"
    ):
        raise AssertionError()


def test_RymUrlAdvanced():
    RymUrlTest = RymUrl.RymUrl()
    RymUrlTest.url_part_type += "everything"
    RymUrlTest.url_part_origin_countries += "France"
    RymUrlTest.url_part_year += "2010s"
    RymUrlTest.url_part_genres += "Rock"
    if (
        str(RymUrlTest)
        != "https://rateyourmusic.com/customchart?chart_type=top&type=everything&year=2010s&genre_include=1&include_child_genres=1&genres=Rock&include_child_genres_chk=1&include_both&origin_countries=France&limit=none&countries=&page=1"
    ):
        raise AssertionError()
