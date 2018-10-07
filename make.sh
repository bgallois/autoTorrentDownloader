#!/bin/bash
if [ -d dist ]; then rm -Rf dist; fi
pyinstaller --add-data 'series.txt:.' check.py 
mv dist/check dist/autoTorrentDownloader

