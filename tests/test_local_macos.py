from pprint import pprint

import pytest

from hostz.local import Local

@pytest.fixture
def local():
    return Local(workspace='/Users/superhin/Projects/ChainMaker/chainmaker-cryptogen')


class TestLocalMacOS:
    def test_exists(self, local):
        assert local.exists(__file__) is True

    def test_check_process(self, local):
        print(local.check_process('python'))


    def test_git_stat_commit_lines(self, local):
        result = local.git_stat_commit_lines()
        pprint(result)

    def test_git_stat_commits(self, local):
        result = local.git_stat_commits()
        pprint(result)

