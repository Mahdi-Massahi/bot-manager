#!/bin/bash

# nebixbm -ta &&
pip3 install -r requirements.txt &&
pip3 install --upgrade --force-reinstall . &&
nebixbm -v -oo &&
echo "hi"
