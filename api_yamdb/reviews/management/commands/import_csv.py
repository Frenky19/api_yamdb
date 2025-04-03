# Это скрипт, копирующий данные из csv в бд, но тесты не пропустили

# import os

# import pandas as pd
# from django.core.management.base import BaseCommand

# from reviews.models import Category, Comment, Genre, Review, Title
# from users.models import User

# DATA_DIR = 'static/data'


# class Command(BaseCommand):
#     help = "Загружает данные из файлов CSV в базу данных"

#     def load_csv(self, file_name):
#         """
#         Загружает CSV-файл в DataFrame.

#         Если файл отсутствует, выводит сообщение об ошибке.
#         """
#         file_path = os.path.join(DATA_DIR, file_name)
#         if not os.path.exists(file_path):
#             self.stdout.write(self.style.ERROR(
#                 f'Файл {file_name} не найден в директории {DATA_DIR}'))
#             return None
#         return pd.read_csv(file_path)

#     def handle(self, *args, **kwargs):
#         self.stdout.write('Начинаем загрузку данных...')

#         # Загрузка категорий
#         self.stdout.write('Загрузка категорий...')
#         category_data = self.load_csv('category.csv')
#         if category_data is not None:
#             for _, row in category_data.iterrows():
#                 Category.objects.get_or_create(
#                     id=row['id'],
#                     name=row['name'],
#                     slug=row['slug'],
#                 )
#             self.stdout.write(self.style.SUCCESS(
#                 f'Загружено {len(category_data)} категорий.'))

#         # Загрузка жанров
#         self.stdout.write('Загрузка жанров...')
#         genre_data = self.load_csv('genre.csv')
#         if genre_data is not None:
#             for _, row in genre_data.iterrows():
#                 Genre.objects.get_or_create(
#                     id=row['id'],
#                     name=row['name'],
#                     slug=row['slug'],
#                 )
#             self.stdout.write(self.style.SUCCESS(
#                 f'Загружено {len(genre_data)} жанров.'))

#         # Загрузка произведений (titles)
#         self.stdout.write('Загрузка произведений...')
#         title_data = self.load_csv('titles.csv')
#         if title_data is not None:
#             for _, row in title_data.iterrows():
#                 category = Category.objects.get(id=row['category'])
#                 Title.objects.get_or_create(
#                     id=row['id'],
#                     name=row['name'],
#                     year=row['year'],
#                     category=category,
#                 )
#             self.stdout.write(self.style.SUCCESS(
#                 f'Загружено {len(title_data)} произведений.'))

#         # Загрузка связей (genre_title)
#         self.stdout.write('Загрузка связей жанров и произведений...')
#         genre_title_data = self.load_csv("genre_title.csv")
#         if genre_title_data is not None:
#             for _, row in genre_title_data.iterrows():
#                 title = Title.objects.get(id=row['title_id'])
#                 genre = Genre.objects.get(id=row['genre_id'])
#                 title.genre.add(genre)
#             self.stdout.write(self.style.SUCCESS(
#                 f'Загружено {len(genre_title_data)}'
#                 'связей жанров и произведений.'
#             ))

#         # Загрузка пользователей
#         self.stdout.write('Загрузка пользователей...')
#         user_data = self.load_csv('users.csv')
#         if user_data is not None:
#             for _, row in user_data.iterrows():
#                 User.objects.get_or_create(
#                     id=row['id'],
#                     username=row['username'],
#                     email=row['email'],
#                     role=row['role'],
#                     bio=row['bio'] if not pd.isnull(row['bio']) else '',
#                     first_name=row['first_name'] if not pd.isnull(
#                         row['first_name']) else '',
#                     last_name=row['last_name'] if not pd.isnull(
#                         row['last_name']) else '',
#                 )
#             self.stdout.write(self.style.SUCCESS(
#                 f'Загружено {len(user_data)} пользователей.'))

#         # Загрузка отзывов
#         self.stdout.write('Загрузка отзывов...')
#         review_data = self.load_csv('review.csv')
#         if review_data is not None:
#             for _, row in review_data.iterrows():
#                 title = Title.objects.get(id=row['title_id'])
#                 author = User.objects.get(id=row['author'])
#                 Review.objects.get_or_create(
#                     id=row['id'],
#                     title=title,
#                     text=row['text'],
#                     author=author,
#                     score=row['score'],
#                     pub_date=row['pub_date'],
#                 )
#             self.stdout.write(self.style.SUCCESS(
#                 f'Загружено {len(review_data)} отзывов.'))

#         # Загрузка комментариев
#         self.stdout.write('Загрузка комментариев...')
#         comment_data = self.load_csv('comments.csv')
#         if comment_data is not None:
#             for _, row in comment_data.iterrows():
#                 review = Review.objects.get(id=row['review_id'])
#                 author = User.objects.get(id=row['author'])
#                 Comment.objects.get_or_create(
#                     id=row['id'],
#                     review=review,
#                     text=row['text'],
#                     author=author,
#                     pub_date=row['pub_date'],
#                 )
#             self.stdout.write(self.style.SUCCESS(
#                 f'Загружено {len(comment_data)} комментариев.'))
#         self.stdout.write(self.style.SUCCESS('Загрузка данных завершена.'))
