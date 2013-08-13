#!/bin/bash

./manage.py inspectdb > ./urqa/models.py
sed -i 's/\.IntegerField(primary_key=True)/.AutoField(primary_key=True)/g' ./client/models.py

cp ./urqa/models.py ./client/models.py
cp ./urqa/models.py ./usermanage/models.py
cp ./urqa/models.py ./projectmanage/models.py

