=================
Viewflow Cookbook
=================

Set of samples projects and receipts for django-material and viewflow

- `Celery <./celery>`_ Viewflow with Celery sample
- `Custom UI <./custom_ui>`_
- `Custom Views <./custom_views>`_
- `Dashboard <./dashboard>`_ Sample dashboard for django-material
- `Frontend <./frontend>`_ Custom compoment sample for django-material
- `Guardian <./guardian>`_ Object-based permissions sample
- `HelloWorld <./helloworld>`_ The tutorial project
- `Subprocess <./subprocess>`_ Viewflow subprocess sample


각 샘플별로... 아래 실행해면 됨.

python -m venv .venv && source .venv/bin/activate

python -m pip install -r requirements.txt --extra-index-url=https://pypi.viewflow.io/

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver 0.0.0.0:8000