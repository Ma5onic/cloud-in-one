cloud-in-one
============

Local integration of cloud storage services

Travis CI Status:
[![Build Status](https://travis-ci.org/fawques/cloud-in-one.svg?branch=master)](https://travis-ci.org/fawques/cloud-in-one)

<h2>Installing sources</h2>
<h3>Software needed</h3>
- Python 3.4.2
- Dropbox SDK package ==> `pip install dropbox`
- Dataset package ==> `pip install dataset`
For testing:
- Nose package ==> `pip install nose`


<h3>PowerShell VirtualEnv</h3>
To create a venv:
`python.exe <Path to python>\Tools\Scripts\pyvenv.py <venv-path>`
To activate it:

    Set-ExecutionPolicy RemoteSigned
    <venv-path>\Scripts\Activate.ps1

<h2>Running tests</h2>
`nosetests`
