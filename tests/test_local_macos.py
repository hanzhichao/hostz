

import pytest

from hostz.local import Local

@pytest.fixture
def local():
    return Local()


class TestLocalMacOS:
    def test_exists(self, local):
        assert local.exists(__file__) is True

    def test_check_process(self, local):
        print(local.check_process('python'))

