import pytest
import os


@pytest.mark.skipif(
    "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
    reason="doesn't work with Travis",
)
def test_album_infos(network):
    url_album = "https://rateyourmusic.com/release/album/everything-everything/get-to-heaven-2/"

    album_infos = network.get_album_infos(url_album)

    if album_infos["Name"] != "Get to Heaven":
        raise AssertionError()

    if album_infos["Artist"] != "Everything Everything":
        raise AssertionError()

    if (
        album_infos["Descriptors"]
        != "energetic,  anxious,  war,  playful,  political,  conscious,  apocalyptic,  satirical,  angry,  existential,  rhythmic,  male vocals,  progressive,  violence,  quirky,  melodic"
    ):
        raise AssertionError()

    if (
        album_infos["Genres"]
        != "Progressive Pop, Art Pop\nIndietronica, New Wave, Alternative Dance"
    ):
        raise AssertionError()

    if album_infos["Language"] != "English":
        raise AssertionError()

    if album_infos["Released"] != "22 June 2015":
        raise AssertionError()

    if album_infos["Type"] != "Album":
        raise AssertionError()
