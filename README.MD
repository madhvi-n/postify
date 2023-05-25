# Postify

A Django application to create posts which utilizes Graphql


## Features
- Users can create, edit, and delete posts.
- Users can create, edit, and delete comments on posts.
- Users can archive a post.
- Users can feature a post.
- Users can disable comments on their posts.
- Users can add categories to their posts.
- Users can add tags to their posts.


## Requirements
- Python 3.8+


## Installation
- Clone the repository and enter the root directory
  ```
  git clone https://github.com/madhvi-n/postify.git
  cd postify
  ```
- Create a virtual environment and activate it
  ```
  virtualenv venv --python=python3
  source venv/bin/activate
  ```

- Install the Python dependencies
  ```
  pip install -r requirements.txt
  ```

- Run the database migrations
  ```
  python manage.py migrate
  ```

- Create a python superuser account
  ```
  python manage.py createsuperiser
  ```

- Start your Django server
  ```
  python manage.py runserver
  ```

- Access the Django admin UI on `http://127.0.0.1:8000/admin/ or localhost:8000/admin`

- Access the Graphql UI on `http://127.0.0.1:8000/graphql/ or localhost:8000/graphql`
