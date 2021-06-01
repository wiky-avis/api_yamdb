from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLES = [
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор')
    ]

    email = models.EmailField(
        'Адрес электронной почты', unique=True, db_index=True,)
    role = models.CharField(
        'Права', max_length=10, choices=ROLES, default='user')
    bio = models.TextField('О себе', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Category(models.Model):
    pass


class Genre(models.Model):
    pass


class Title(models.Model):
    pass


class Review(models.Model):
    title_id = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Отзыв',
        help_text='Оставьте отзыв'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )
    text = models.TextField()
    score = models.IntegerField(
        choices=(
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5'),
            (6, '6'),
            (7, '7'),
            (8, '8'),
            (9, '9'),
            (10, '10'),
        )
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
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )
    text = models.TextField()

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]
