from distutils.core import setup
import py2exe

setup(
    options={'py2exe': {'bundle_files': 1, "includes": ["sqlalchemy.dialects.sqlite"], "excludes": ["six.moves.urllib.parse"]}},
    #windows = [{'script': "hello.py"}],
    console=[{
        ### Main Python script
        "script": "main.py",
        # "icon_resources": [(0, "favicon.ico")], ### Icon to embed into the PE file.
        "dest_base": "cloud-in-one"
    }, {
        ### Main Python script
        "script": "main_crypto.py",
        # "icon_resources": [(0, "favicon.ico")], ### Icon to embed into the PE file.
        "dest_base": "cio-crypt"
    }],
    zipfile=None,
    data_files=[('config', ['config/config.json', 'config/log.json']), ('', ['trusted-certs.crt'])]
)
