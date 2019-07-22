#!/usr/bin/env bash
PIP3_exists="$(which pip3)"
PIP_exists="$(which pip)"
if [ ! -z $PIP3_exists ]
then
    pip3 install ../dist/mc_server_manager-0.1.0.tar.gz
else
    if [ ! -z $PIP_exists ]
    then
        pip install ../dist/mc_server_manager-0.1.0.tar.gz
    else
        echo "No version of pip installed on system. Please ensure python3 and pip are installed"
    fi
fi