import manager
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises
from nose.tools import assert_true
from nose.tools import assert_false


class TestManager(object):
    def __init__(self):
        pass

    def test_manager(self):
        man = manager.Manager('user', 'password')
        assert_false(man is None)

    def test_newAccount_dropbox(self):
        man = manager.Manager('user', 'password')
        man.newAccount('dropbox_stub', 'user')
        assert_true(man.cuentas)
