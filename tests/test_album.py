import pytest
import os


@pytest.mark.skipif(
    "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
    reason="doesn't work with Travis",
)
def test_album_infos(network):
    url_album = (
        "https://rateyourmusic.com/release/album/everything-everything/get-to-heaven-2/"
    )

    album_infos = network.get_album_infos(url_album)

    if album_infos["Name"] != "Get to Heaven":
        raise AssertionError()

    if album_infos["Artist"] != "Everything Everything":
        raise AssertionError()

    if not (
        all(
            x
            for x in ["anxious", "energetic", "playful", "conscious", "satirical"]
            if x in album_infos["Descriptors"]
        )
    ):
        raise AssertionError()

    print(album_infos)
    if (
        album_infos["Genres"]
        != "Art Pop, Progressive Pop, Indie Rock\nIndietronica, Alternative Dance, New Wave"
    ):
        raise AssertionError()

    if album_infos["Language"] != "English":
        raise AssertionError()

    if album_infos["Released"] != "22 June 2015":
        raise AssertionError()

    if album_infos["Type"] != "Album":
        raise AssertionError()

    if album_infos["Track listing"] != [
        "To the Blade",
        "Distant Past",
        "Get to Heaven",
        "Regret",
        "Spring / Sun / Winter / Dread",
        "The Wheel (Is Turning Now)",
        "Fortune 500",
        "Blast Doors",
        "Zero Pharaoh",
        "No Reptiles",
        "Warm Healer",
    ]:
        raise AssertionError()

    if album_infos["Colorscheme"] != [
        "#f47b50",
        "#8da3c8",
        "#242960",
        "#3b488c",
        "#cd2769",
        "#fab43b",
        "#b97d49",
        "#ac1e68",
        "#3a53a7",
    ]:
        raise AssertionError()
