#!/bin/bash
fuser -k 8000/tcp
./manage.py runserver 0.0.0.0:8000 2>&1 | tee debuglog.txt
