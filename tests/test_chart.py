import pytest
import os
from rymscraper import RymUrl


@pytest.mark.skipif(
    "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
    reason="doesn't work with Travis",
)
def test_chart_infos(network):
    url = RymUrl.RymUrl()
    page_size = 40
    max_page = 2

    chart_infos = network.get_chart_infos(url, max_page=max_page)
    print(len(chart_infos))

    if not len(chart_infos) == max_page * page_size:
        raise AssertionError()

    first_item = chart_infos[0]
    second_page_item = chart_infos[page_size]

    if not first_item["Rank"] == "1":
        raise AssertionError()

    if not second_page_item["Rank"] == str(page_size + 1):
        raise AssertionError()

    if not first_item["Artist"] == "Radiohead":
        raise AssertionError()

    if not first_item["Album"] == "OK Computer":
        raise AssertionError()

    if not first_item["Date"] == "16 June 1997":
        raise AssertionError()

    if not first_item["Genres"] == "Alternative Rock, Art Rock":
        raise AssertionError()

    if (
            not isinstance(first_item["RYM Rating"], str)
            and "." in first_item["RYM Rating"]
    ):
        raise AssertionError()

    if not isinstance(first_item["Ratings"], str):
        raise AssertionError()

    if not isinstance(first_item["Reviews"], str):
        raise AssertionError()
