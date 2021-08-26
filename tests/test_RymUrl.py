from rymscraper import RymUrl


def test_RymUrlSimple():
    RymUrlTest = RymUrl.RymUrl()
    print(str(RymUrlTest))
    if str(RymUrlTest) != "https://rateyourmusic.com/charts/top/album/1/":
        raise AssertionError()


def test_RymUrlAdvanced():
    RymUrlTest = RymUrl.RymUrl()
    RymUrlTest.url_part_type = "/release"
    RymUrlTest.url_part_origin_countries = "/loc:france"
    RymUrlTest.url_part_year = "/2010s"
    RymUrlTest.url_part_genres += "/g:rock"
    print(str(RymUrlTest))
    if (
        str(RymUrlTest)
        != "https://rateyourmusic.com/charts/top/release/2010s/g:rock/loc:france/1/"
    ):
        raise AssertionError()
