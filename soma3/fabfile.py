from fabric.api import local,task, run

@task
def runserver():
    local('python manage.py runserver 0.0.0.0:9001')

@task
def test():
    local('python manage.py test')

