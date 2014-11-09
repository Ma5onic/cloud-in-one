import manager as man

#def test_fail():
#    assert True == False


def test_Ok():
    assert True is True


def test_manager():
    manager = man.Manager('user', 'password')
    assert manager.newAccount('DBStub', 'user') is True
    assert manager.deleteAccount('user') is True
