import pytest
import os


@pytest.mark.skipif(
    "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
    reason="doesn't work with Travis",
)
def test_artist_infos(network):
    url_artist = "https://rateyourmusic.com/artist/pinback"

    artist_infos = network.get_artist_infos(url_artist)

    if artist_infos["Name"] != "Pinback":
        raise AssertionError()

    if artist_infos["Formed"] != "January 1998, San Diego, CA, United States":
        raise AssertionError()

    if artist_infos["Genres"] != "Indie Rock, Indie Pop":
        raise AssertionError()

    if (
        artist_infos["Members"]
        != "Rob Crow (vocals, guitar, bass), Armistead Burwell Smith IV (vocals, bass, keyboards)"
    ):
        raise AssertionError()
