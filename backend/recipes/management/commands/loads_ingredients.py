import json
import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from recipes.models import Ingredient

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('filename', default='ingredients.json', nargs='?',
                            type=str)

    def handle(self, *args, **options):
        logging.info('скрипт переноса в бд запустился')
        try:
            with open(os.path.join(DATA_ROOT, options.get('filename')), 'r',
                      encoding='utf-8') as file_data_json:
                data_ingredient = json.load(file_data_json)
                logging.info('Загрузка ингредиентов началась')
                try:
                    Ingredient.objects.bulk_create(
                        Ingredient(**items) for items in data_ingredient
                    )
                except IntegrityError:
                    logging.info('Ингредиенты уже были загружены')
        except FileNotFoundError as err:
            raise CommandError('Файл отсутствует в директории data') from err
