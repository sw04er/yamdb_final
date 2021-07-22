from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

from .managers import UserManager
from .validators import year_validator


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user'
        MODERATOR = 'moderator'
        ADMIN = 'admin'

    email = models.EmailField(unique=True)
    role = models.CharField(
        verbose_name='Role',
        max_length=50,
        choices=Role.choices,
        default=Role.USER
    )
    bio = models.CharField(
        verbose_name='Биография',
        max_length=255,
        blank=True,
        null=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True,
        null=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.email}||{self.username}||{self.role}'

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR


class UserToRegister(models.Model):
    email = models.EmailField(
        unique=True,
        primary_key=True
    )
    confirmation_code = models.UUIDField(
        verbose_name='Код подтверждения',
        blank=True,
        null=True
    )


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название категории',
        help_text='Введите название категории',
        db_index=True
    )
    slug = models.SlugField(
        unique=True,
        max_length=100,
        verbose_name='Идентификатор страницы категории',
        help_text='Slug должен быть уникальным и не превышать 100 символов',

    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название жанра',
        help_text='Введите название жанра',
    )
    slug = models.SlugField(
        unique=True,
        max_length=100,
        verbose_name='Идентификатор страницы жанра',
        help_text='Slug должен быть уникальным и не превышать 100 символов',
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название произведения',
        help_text='Введите название произведения',
    )
    year = models.IntegerField(
        verbose_name='Год выхода произведения',
        help_text='Введите год выхода произведения',
        blank=True,
        null=True,
        validators=[year_validator]
    )

    description = models.TextField(
        verbose_name='Описание произведения',
        help_text='Введите описание произведения',
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Название жанра',
        help_text='Вы можете выбрать жанр для этого произведения',
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        related_name='titles',
        verbose_name='Название категории',
        help_text='Вы можете выбрать категорию для этого произведения',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='reviews')
    score = models.PositiveIntegerField(validators=[MaxValueValidator(10),
                                                    MinValueValidator(1)])
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-id', '-pub_date']

    def __str__(self):
        return str(self.pk)


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id', '-pub_date']

    def __str__(self):
        return str(self.pk)
