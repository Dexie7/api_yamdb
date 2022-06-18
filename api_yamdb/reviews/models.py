from django.utils import timezone
from django.core.validators import (MaxValueValidator)
from django.db import models


class User


class Category(models.Model):
    name = models.CharField(
        max_length=30,
        verbose_name='Категория'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Адрес'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=30,
        verbose_name='Жанр'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Адрес'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Произведение',
    )
    year = models.IntegerField(
        verbose_name='Дата выхода',
        validators=(MaxValueValidator(
            timezone.now().year,
            message='Год не может быть больше текущего!'),)
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField(
        verbose_name='Текст отзыва',
    )
    score = models.IntegerField(
        verbose_name='Оценка',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Название произведения',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = [['title', 'author']]

    def __str__(self):
        return self.text


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )

    class Meta:
        verbose_name = 'Комментрарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
