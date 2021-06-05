from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


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
    name = models.CharField(max_length=40, verbose_name='Категория')
    slug = models.SlugField(max_length=40, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id', ]


class Genre(models.Model):
    name = models.CharField(max_length=40, verbose_name='Жанр')
    slug = models.SlugField(max_length=40, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id', ]


class Title(models.Model):
    name = models.CharField(
        max_length=100,
        db_index=True,
        blank=False,
        null=False,
        unique=True,
        verbose_name='Название произведения',
    )
    year = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Год производства',
    )
    description = models.TextField(blank=True)
    rating = models.IntegerField(blank=True, null=True)
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        db_index=True,
        verbose_name='Жанр произведения'
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
    title_id = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Отзыв',
        help_text='Оставьте отзыв'
    )
    text = models.TextField()
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(10)
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title_id', 'author'],
                name='already_review',
            )
        ]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    review_id = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий',
        help_text='Напишите комментарий'
    )
    text = models.TextField()
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]
