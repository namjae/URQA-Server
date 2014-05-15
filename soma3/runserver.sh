#!/bin/bash
fuser -k 9001/tcp
./manage.py runserver 0.0.0.0:9001 2>&1 | tee debuglog.txt
