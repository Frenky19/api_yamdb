import os

import pandas as pd
from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

DATA_DIR = 'static/data'


class Command(BaseCommand):
    help = "Загружает данные из файлов CSV в базу данных"

    def _load_csv(self, file_name):
        """Загрузка CSV-файла с обработкой ошибок."""
        file_path = os.path.join(DATA_DIR, file_name)
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(
                f'Файл {file_name} не найден в директории {DATA_DIR}'))
            return None
        return pd.read_csv(file_path)

    def _process_category(self, row):
        Category.objects.get_or_create(
            id=row['id'],
            name=row['name'],
            slug=row['slug'],
        )

    def _process_genre(self, row):
        Genre.objects.get_or_create(
            id=row['id'],
            name=row['name'],
            slug=row['slug'],
        )

    def _process_title(self, row):
        category = Category.objects.get(id=row['category'])
        Title.objects.get_or_create(
            id=row['id'],
            name=row['name'],
            year=row['year'],
            category=category,
        )

    def _process_genre_title(self, row):
        title = Title.objects.get(id=row['title_id'])
        genre = Genre.objects.get(id=row['genre_id'])
        title.genre.add(genre)

    def _process_user(self, row):
        User.objects.get_or_create(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            role=row['role'],
            bio=row['bio'] if not pd.isnull(row['bio']) else '',
            first_name=row['first_name'] if not pd.isnull(
                row['first_name']) else '',
            last_name=row['last_name'] if not pd.isnull(
                row['last_name']) else '',
        )

    def _process_review(self, row):
        title = Title.objects.get(id=row['title_id'])
        author = User.objects.get(id=row['author'])
        Review.objects.get_or_create(
            id=row['id'],
            title=title,
            text=row['text'],
            author=author,
            score=row['score'],
            pub_date=row['pub_date'],
        )

    def _process_comment(self, row):
        review = Review.objects.get(id=row['review_id'])
        author = User.objects.get(id=row['author'])
        Comment.objects.get_or_create(
            id=row['id'],
            review=review,
            text=row['text'],
            author=author,
            pub_date=row['pub_date'],
        )

    def _load_data(self, file_name, processor, model_name):
        """Общая логика загрузки данных для разных моделей."""
        self.stdout.write(f'Загрузка {model_name}...')
        data = self._load_csv(file_name)
        if data is None:
            return
        processor_func = getattr(self, f'_process_{processor}')
        for _, row in data.iterrows():
            processor_func(row)
        self.stdout.write(self.style.SUCCESS(
            f'Загружено {len(data)} {model_name}.'))

    def handle(self, *args, **options):
        self.stdout.write('Начинаем загрузку данных...')
        load_sequence = [
            ('category.csv', 'category', 'категорий'),
            ('genre.csv', 'genre', 'жанров'),
            ('titles.csv', 'title', 'произведений'),
            ('genre_title.csv', 'genre_title', 'связей жанров и произведений'),
            ('users.csv', 'user', 'пользователей'),
            ('review.csv', 'review', 'отзывов'),
            ('comments.csv', 'comment', 'комментариев'),
        ]
        for file_name, processor, model_name in load_sequence:
            self._load_data(file_name, processor, model_name)
        self.stdout.write(self.style.SUCCESS('Загрузка данных завершена.'))
