from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from titles.validators import year_validator


class CustomUser(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор')
    ]

    email = models.EmailField(
        'Адрес электронной почты', unique=True, db_index=True,)
    role = models.CharField(
        'Права', max_length=10, choices=ROLES, default=USER)
    bio = models.TextField('О себе', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR


class Category(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название категории')
    slug = models.SlugField(max_length=40, unique=True)

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=40, verbose_name='Имя жанра')
    slug = models.SlugField(max_length=40, unique=True)

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=100,
        db_index=True,
        unique=True,
        verbose_name='Название произведения',
    )
    year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[year_validator],
        verbose_name='Год производства',
    )
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        db_index=True,
        verbose_name='Жанр произведения',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles',
        verbose_name='Категория произведения',
    )

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Отзыв',
        help_text='Оставьте отзыв',
    )
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            validators.MinValueValidator(
                1, 'Оценка должна быть в диапазоне от 1 до 10'),
            validators.MaxValueValidator(
                10, 'Оценка должна быть в диапазоне от 1 до 10')
        ],
        verbose_name='Оценка',
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='already_review',
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий',
        help_text='Напишите комментарий'
    )
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]
