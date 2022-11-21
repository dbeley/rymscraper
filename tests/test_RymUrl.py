from rymscraper import RymUrl


def test_RymUrlSimple():
    RymUrlTest = RymUrl.RymUrl()
    print(str(RymUrlTest))
    if str(RymUrlTest) != "https://rateyourmusic.com/charts/top/album/1/":
        raise AssertionError()


def test_RymUrlAdvanced():
    RymUrlTest = RymUrl.RymUrl(kind="release", origin_countries="france", year="2010s", genres="rock")

    print(str(RymUrlTest))
    if (
        str(RymUrlTest)
        != "https://rateyourmusic.com/charts/top/release/2010s/g:rock/loc:france/1/"
    ):
        raise AssertionError()
