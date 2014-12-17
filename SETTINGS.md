####This is Settings File for virtualenv

---

- pip install virtualenv
- pip install virtualenvwrapper
- export PATH=$PATH:/usr/local/mysql/bin/

- source /usr/local/bin/virtualenvwrapper.sh 를 .bashrc 나 .profile 에 추가

####initial Setting

- mkvirtualenv urqa
- pip install -r requirements.txt

####active virtualenv working

- workon urqa

####deactive virtualenv

- deactive

#### before run server
- export DYLD_LIBRARY_PATH=/usr/local/mysql/lib/



