from rymscraper import RymNetwork
import pytest


@pytest.fixture
def network():
    return RymNetwork()
