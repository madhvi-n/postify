.PHONY: migrate runserver

migrate:
	python manage.py migrate

createsuperuser:
	python manage.py createsuperuser

runserver:
	python manage.py runserver

format:
	black .
