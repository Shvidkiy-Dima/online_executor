#!/bin/sh


python -m pyls --port 8000 -v &
cd language_proxy
./start.sh