from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class Region(models.Model):
    name = models.CharField('Название', max_length=120, unique=True)
    description = models.TextField('Описание')
    administrative_center = models.CharField('Административный центр', max_length=120)
    area = models.FloatField('Площадь (км²)')
    population = models.PositiveIntegerField('Население')
    image = models.ImageField('Изображение', upload_to='regions/', blank=True, null=True)

    class Meta:
        verbose_name = 'Область'
        verbose_name_plural = 'Области'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('region_detail', kwargs={'pk': self.pk})


class GeographicObject(models.Model):
    class ObjectType(models.TextChoices):
        MOUNTAIN = 'mountain', 'Горы'
        LAKE = 'lake', 'Озёра'
        RIVER = 'river', 'Реки'
        GORGE = 'gorge', 'Ущелья'
        WATERFALL = 'waterfall', 'Водопады'
        RESERVE = 'reserve', 'Заповедники'
        PASS = 'pass', 'Перевалы'
        CAVE = 'cave', 'Пещеры'

    name = models.CharField('Название', max_length=150)
    description = models.TextField('Описание')
    object_type = models.CharField('Тип объекта', max_length=20, choices=ObjectType.choices)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='geographic_objects', verbose_name='Область')
    location = models.CharField('Местоположение', max_length=200)
    image = models.ImageField('Изображение', upload_to='objects/', blank=True, null=True)
    map_link = models.URLField('Ссылка на карту (Google Maps Embed)', blank=True)
    latitude = models.DecimalField('Широта', max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField('Долгота', max_digits=9, decimal_places=6, blank=True, null=True)

    class Meta:
        verbose_name = 'Географический объект'
        verbose_name_plural = 'Географические объекты'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('object_detail', kwargs={'pk': self.pk})


class Attraction(models.Model):
    name = models.CharField('Название', max_length=150)
    description = models.TextField('Описание')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='attractions', verbose_name='Область')
    image = models.ImageField('Изображение', upload_to='attractions/', blank=True, null=True)

    class Meta:
        verbose_name = 'Достопримечательность'
        verbose_name_plural = 'Достопримечательности'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('attraction_detail', kwargs={'pk': self.pk})


class Quiz(models.Model):
    title = models.CharField('Название', max_length=150)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'
        ordering = ['title']

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name='Тест')
    text = models.CharField('Текст вопроса', max_length=300)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
    text = models.CharField('Текст ответа', max_length=300)
    is_correct = models.BooleanField('Правильный ответ', default=False)

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return self.text

    def clean(self):
        if self.is_correct:
            qs = Answer.objects.filter(question=self.question, is_correct=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError('У вопроса может быть только один правильный ответ.')


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.CharField('О себе', max_length=255, blank=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль: {self.user.username}'
