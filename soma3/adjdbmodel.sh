#!/bin/bash

./manage.py inspectdb > ./urqa/models.py
./manage.py inspectdb > ./client/models.py


sed -i 's/\.IntegerField(primary_key=True)/.AutoField(primary_key=True)/g' ./client/models.py
sed -i 's/\.IntegerField(primary_key=True)/.AutoField(primary_key=True)/g' ./urqa/models.py
