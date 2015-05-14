from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

setup(
    options = {'py2exe': {'bundle_files': 2, "includes": ["pygments.styles.default", "sqlalchemy.dialects.sqlite"]}},
    #windows = [{'script': "hello.py"}],
    console = ["manager.py"],
    zipfile = None,
    data_files = [('config', ['config/config.json', 'config/log.json'])]
)
