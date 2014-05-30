#!/bin/bash
fuser -k 9000/tcp
./manage.py runserver 0.0.0.0:9000 2>&1 | tee debuglog.txt
