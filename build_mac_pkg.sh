#!/usr/bin/env bash

pipenv run pyinstaller -F --hiddenimport=google-api-python-client --hiddenimport=googleapiclient --add-data ./gdrive_audit/library:./library  -c --clean --noconfirm ./gdrive_audit/gdrive_audit.py 

~/bin/pycodesign.py -s -p -n -t ./pycodesign_local.ini
