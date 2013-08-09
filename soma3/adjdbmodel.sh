#!/bin/bash

./manage.py inspectdb > ./urqa/models.py
./manage.py inspectdb > ./client/models.py
