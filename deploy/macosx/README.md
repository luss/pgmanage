# PgManage macOS Build

The build should be done on Windows 10 x86_64 OS.
The following software should be installed prior to runnig the build script:

Official Python 3.9.* macOs release

- Node.js
- npm

## Building
1. Simply run in command line deploy script:
```
./deploy.sh [pgmanage_version]
```
You can specify version number that will be added to bundle and .dmg file.
It defaults to last version tag from git repository.

This will create the python virtual environment and install all the required python modules mentioned in the requirements file using pip, build the runtime code and finally create the app bundle and the DMG in ./release.$pgmanage_version directory.