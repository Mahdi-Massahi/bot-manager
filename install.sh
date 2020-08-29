#!/bin/bash

rm -rf env &&
python3.8 -m venv env/ &&
source env/bin/activate &&
pip3 install -r requirements.txt &&
pip3 install .