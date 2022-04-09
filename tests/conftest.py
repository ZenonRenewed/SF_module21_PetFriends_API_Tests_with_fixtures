import pytest
from api import pf
from settings import valid_email, valid_password


@pytest.fixture()
def get_api_key():
    status, pf.key = pf.get_api_key(valid_email, valid_password)
    assert status == 200
    assert 'key' in pf.key

    yield

    assert pf.status == 200


@pytest.fixture(autouse=True)
def logging():
    logtest = open('log.txt', 'w')
