#!/bin/bash

# nebixbm -ta &&
pip3 install -r requirements.txt &&
pip3 install --upgrade --force-reinstall . &&
python3 /usr/local/lib/python3.8/site-packages/nebixbm/__main__.py -v
