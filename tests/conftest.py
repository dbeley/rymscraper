from rymscraper import rymscraper
import pytest


@pytest.fixture(scope="session", autouse=True)
def network():
    network = rymscraper.RymNetwork(headless=True)
    yield network
    network.browser.close()
    network.browser.quit()
