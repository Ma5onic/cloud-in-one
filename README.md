CLOUD-IN-ONE
==============

Travis CI Status:
[![Build Status](https://travis-ci.org/vguzmanp/cloud-in-one.svg?branch=master)](https://travis-ci.org/vguzmanp/cloud-in-one)

CLOUD-IN-ONE is a project oriented to provide a secure and transparent interface to cloud storage services.

We achieve this with an application that syncs in background all files in the sync folder with all accounts linked. The process is similar to the one used by the Dropbox official client, but linked to different accounts.
In addition, all files from each storage service is aggregated into the same folder in a transparent way for the user, so he doesn't need to know what service he is uploading each file.

The system can encrypt files before uploading them to the services. Thus, in case anyone got access to the remote account (for instance, from the Dropbox website) thay couldn't read any of the files.

¿Why CLOUD-IN-ONE?
----------------------
- I have several Dropbox accounts and I want to sync them in the same PC, but the offcial client only allows one account per PC.
- I have several cloud storage accounts. My files fit in the total storage size, but they don't fit in any separated account.
- I have a storage service aggegator, but I don't want to need to know which account is holding which file.
- I don't trust my storage provider won't read my private information that I upload to their service.
- I don't trust someone will get access to my storage account and will be able to read my files.
- I want an open-source alternative to the cloud sync applications.

Comparison with similar applications:
------------------------------
I may seem that there are many services and apps that do exactly what CLOUD-IN-ONE does, but:
- Unlike the official *Dropbox* client, CLOUD-IN-ONE allows you to link more than one account to the same PC.
- CLOUD-IN-ONE is integrated with the Operating System: the user only needs to worry about saving his files in a local folder, and the application will be in charge of monitoring it and uploading the files to a remote service. Other applications such as *Jolicloud*, *CloudKafé* or *MultCloud* are web based, so the user will be forced to work from the browser and not from the OS itself.
- Services such as *Gladinet*, *odrive* or *otixo* split the services in different folders, CLOUD-IN-ONE aggregates all accounts in the same folder. This way the user saves his files in the folder, and CLOUD-IN-ONE will organize the files in the services.
- CLOUD-IN-ONE allows you to encrypt your files before uploading, so that no one unauthorized can read them.

Problems:
--------------------
- Third-party API dependance.
- Files spread out in several services.
- When encryption is activated for a file, it may be more difficult to access to it in a platform where the application isn't installed.

<h2>Installing from source</h2>
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
