
import os
from csv import DictReader
from django.core.management import BaseCommand
from posts.models import Ingredients

class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_file_path = os.path.join(os.path.dirname(__file__), 'data', 'ingredients.csv')
        counter = 0
        for row in DictReader(open(csv_file_path, encoding='utf-8'), fieldnames=['name', 'measurement_unit']):
            ingredient = Ingredients(
                name=row['name'],
                measurement_unit=row['measurement_unit']
            )
            ingredient.save()
            print(f'"{ingredient}" - добавлен в базу данных.')
            counter += 1
        print(f'Загружено {counter} ингредиентов.')