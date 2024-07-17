import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('Жанр')
        verbose_name_plural = _('Жанры')

class Gender(models.TextChoices):
    MALE = 'male', _('male')
    FEMALE = 'female', _('female')

class FilmWork(UUIDMixin, TimeStampedMixin):
    MOVIE_TYPE_CHOICES = [
        ("movie", _("Movie")),
        ("tv_show", _("TV Show")),
    ]
    certificate = models.CharField(_('certificate'), max_length=512, blank=True)
    file_path = models.FileField(_('file'), blank=True, null=True, upload_to='movies/')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creation_date = models.DateField()
    type = models.CharField(max_length=15, choices=MOVIE_TYPE_CHOICES, default="movie")
    rating = models.FloatField(_('rating'), blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('Фильм')
        verbose_name_plural = _('Фильмы')

    def __str__(self):
        return f"{self.title} ({self.type})"

class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(max_length=200)

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('Человек')
        verbose_name_plural = _('Люди')

class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        unique_together = ('film_work', 'genre')

class PersonFilmwork(UUIDMixin, TimeStampedMixin):
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.TextField(_('role'), null=True)
    gender = models.TextField(_('gender'), choices=Gender.choices, null=True)

    class Meta:
        db_table = "content\".\"person_film_work"
