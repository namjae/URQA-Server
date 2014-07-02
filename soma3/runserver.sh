#!/bin/bash
fuser -k 80/tcp
./manage.py runserver 0.0.0.0:80 2>&1 | tee debuglog.txt
