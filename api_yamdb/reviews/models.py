from datetime import datetime as dt
from collections import namedtuple

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

ROLES_NAME = namedtuple('ROLES_NAME', 'user moderator admin')
ROLES = ROLES_NAME('user', 'moderator', 'admin')
ROLE_CHOICES = (
    ('user', ROLES.user),
    ('moderator', ROLES.moderator),
    ('admin', ROLES.admin),
)


class User(AbstractUser):
    """Модель пользователей."""
    email = models.EmailField(
        'email пользователя',
        blank=False,
        unique=True,
        max_length=254,
    )
    first_name = models.CharField(
        'first name',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        'first name',
        max_length=150,
        blank=True
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль пользователя',
        max_length=max(len(role) for _, role in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=ROLES.user,
    )

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def is_moderator(self):
        return self.role == ROLES.moderator

    def is_admin(self):
        return (
            self.role == ROLES.admin
            or self.is_staff
        )

    def str(self):
        return self.username


class BaseCategoryGenre(models.Model):
    """Базовый класс для категорий и жанров."""
    name = models.CharField(
        max_length=256,
        db_index=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name='Удобочитаемая метка URL',
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def str(self):
        return self.name[:20]


class Category(BaseCategoryGenre):
    """Категории произведений."""

    class Meta(BaseCategoryGenre.Meta):
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'


class Genre(BaseCategoryGenre):
    """Жанры произведений."""

    class Meta(BaseCategoryGenre.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Произведения, к которым пишут отзывы (Review)."""
    name = models.CharField(
        max_length=256,
        verbose_name='Произведение'
    )
    year = models.IntegerField(
        validators=(
            MaxValueValidator(
                limit_value=dt.now().year,
                message='Недопустимы невышедшие произведения'),
        ),
        verbose_name='Год создания произведения'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр произведения'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles'
    )
    description = models.TextField(verbose_name='Описание')

    class Meta:
        ordering = ['name']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def str(self):
        return self.name


class BaseReviewComment(models.Model):
    """Базовая модель ревью и комментариев."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)ss'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата',
    )

    class Meta:
        abstract = True

    def str(self):
        return self.text[:20]


class Review(BaseReviewComment):
    """Отзывы на произведения."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews')
    score = models.IntegerField(
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ],
        verbose_name='Рейтинг произведения'
    )

    class Meta:
        ordering = ['title']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]
        verbose_name = 'Ревью'
        verbose_name_plural = 'Ревью'


class Comment(BaseReviewComment):
    """Комментарии к отзыву."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    class Meta:
        ordering = ['review']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
