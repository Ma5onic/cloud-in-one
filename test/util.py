from nose.tools import assert_equal
from nose.tools import assert_greater_equal
from nose.tools import assert_true


def Ignore(fn):
    def ignoreTest(self):
        pass
    return ignoreTest


def returnFalse(*args, **kwargs):
    ''' This function ignores all arguments, and always returns false '''
    return False


def compareChangeLists(changeList, expected_changeList):
    changeList = sorted(set(i.items()) for i in changeList)
    expected_changeList = sorted(set(i.items()) for i in expected_changeList)

    assert_greater_equal(changeList, expected_changeList)
    assert_equal(len(changeList), len(expected_changeList))
    # assert_true(expected_changeList <= changeList)
