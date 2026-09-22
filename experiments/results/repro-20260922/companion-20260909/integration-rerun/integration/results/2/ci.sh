#!/bin/sh
set -eu
python3 validate-gates.py
dispat run tests --since all
dispat
