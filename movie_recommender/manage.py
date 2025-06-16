#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_recommender.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

# Requirements
# django: pip install django
# Pillow: pip install pillow

# "python manage.py runserver" to start the server

# Import data to the database
# python manage.py makemigrations
# python manage.py migrate
# python manage.py shell
# exec(open('load_movies.py').read())

# The data should have following structure
# recommender_systems/movie_recommender/datasets/information/ (https://drive.google.com/file/d/1je77e0Lq8naVUsjoOzk5RuI2H3ceHlSz/view rename the folder you download to information)
# recommender_systems/movie_recommender/datasets/posters/ (https://www.kaggle.com/ghrzarea/movielens-20m-posters-for-machine-learning rename this folder you download to posters)
# datasets folder should be on the same level as load_movies.py
# Don't delete 0.png in datasets/posters/


# 185 x 278 image format