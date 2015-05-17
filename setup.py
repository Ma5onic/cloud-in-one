from distutils.core import setup
import py2exe

setup(
    options = {'py2exe': {'bundle_files': 1, "includes": ["sqlalchemy.dialects.sqlite"], "excludes": ["six.moves.urllib.parse"]}},
    #windows = [{'script': "hello.py"}],
    console = ["manager.py"],
    zipfile = None,
    data_files = [('config', ['config/config.json', 'config/log.json']), ('', ['trusted-certs.crt'])]
)
