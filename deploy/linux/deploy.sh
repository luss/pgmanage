#!/bin/bash

docker run -e VERSION="$1" -v $PWD:/tmp --rm pgmanage/tarbuild

sudo chown $USER:$USER *.tar.gz
sudo chown $USER:$USER *.AppImage
# sudo chown $USER:$USER *.deb
# sudo chown $USER:$USER *.rpm
