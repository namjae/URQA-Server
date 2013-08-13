#!/bin/bash
/etc/init.d/smbd restart
./manage.py runserver 0.0.0.0:9000
