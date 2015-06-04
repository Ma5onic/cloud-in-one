from nose.tools import assert_equal
from nose.tools import assert_greater_equal
from nose.tools import assert_true
from exceptions import RetryException, FullStorageException, APILimitedException, UnknownError


def Ignore(fn):
    def ignoreTest(self):
        pass
    return ignoreTest


def returnFalse(*args, **kwargs):
    ''' This function ignores all arguments, and always returns false '''
    return False


def returnEmptyList(*args, **kwargs):
    ''' This function ignores all arguments, and always returns [] '''
    return []


def compareChangeLists(changeList, expected_changeList):
    changeList = sorted(set(i.items()) for i in changeList)
    expected_changeList = sorted(set(i.items()) for i in expected_changeList)

    assert_greater_equal(changeList, expected_changeList)
    assert_equal(len(changeList), len(expected_changeList))
    # assert_true(expected_changeList <= changeList)


def compareFileLists(fileList, expected_fileList):
    assert_equal(sorted(fileList), sorted(expected_fileList))


def pre_execute_decorator(previous_fn, fn):
    def wrapped(*args, **kwargs):
        print('This is wrapped')
        previous_fn()
        return fn(*args, **kwargs)
    return wrapped


def raise_first_decorator(fn, exception_to_raise):
    should_raise = True

    def wrapped(*args, **kwargs):
        nonlocal should_raise
        if should_raise:
            should_raise = False
            raise exception_to_raise
        else:
            should_raise = True
            return fn(*args, **kwargs)
    return wrapped


def raise_always_decorator(exception):
    def wrapped(*args, **kwargs):
        raise exception()
    return wrapped
