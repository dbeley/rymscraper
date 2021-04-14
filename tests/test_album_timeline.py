import pytest
import os


@pytest.mark.skipif(
    "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
    reason="doesn't work with Travis",
)
def test_album_infos(network):
    url_album = (
        "https://rateyourmusic.com/release/comp/malicorne/legende___deuxieme_epoque/"
    )

    album_timeline = network.get_album_timeline(url_album)

    if not album_timeline:
        raise AssertionError()

    if len(album_timeline) < 14:
        raise AssertionError()

    if not album_timeline[-1]["Date"] == "13 Aug 2004":
        raise AssertionError()
