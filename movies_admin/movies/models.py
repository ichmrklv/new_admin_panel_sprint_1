import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'genre'
        verbose_name = _('genre')
        verbose_name_plural = _('genres')
        constraints = [
            models.UniqueConstraint(fields=['name'], name='genre_name_unique')
        ]


class FilmWorkType(models.TextChoices):
    MOVIE = 'movie', _('Movie')
    TV_SHOW = 'tv_show', _('TV Show')


class FilmWork(UUIDMixin, TimeStampedMixin):
    certificate = models.CharField(_('certificate'), max_length=512, blank=True)
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    creation_date = models.DateField(_('creation date'), blank=True, null=True)
    rating = models.FloatField(_('rating'), blank=True,
                            validators=[MinValueValidator(0),
                                        MaxValueValidator(100)]) 
    type = models.CharField(_('type'), max_length=20, choices=FilmWorkType.choices)

    file_path = models.FileField(_('file'), blank=True, null=True, upload_to='movies/')

    genres = models.ManyToManyField(Genre, through='GenreFilmWork')
    persons = models.ManyToManyField('Person', through='PersonFilmWork')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'film_work'
        verbose_name = _('film work')
        verbose_name_plural = _('film works')
        indexes = [
            models.Index(fields=['creation_date'], name='film_work_creation_date_idx'),
            models.Index(fields=['rating'], name='film_work_rating_idx'),
            models.Index(fields=['type'], name='film_work_type_idx'),
        ]


class GenreFilmWork(UUIDMixin):
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'genre_film_work'
        verbose_name = _('genre film work')
        verbose_name_plural = _('genre film works')
        constraints = [
            models.UniqueConstraint(fields=['genre', 'film_work'], name='genre_film_work_unique')
        ]
        indexes = [
            models.Index(fields=['film_work'], name='gfw_fw_id_idx'),
        ]


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(_('full name'))

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'person'
        verbose_name = _('person')
        verbose_name_plural = _('persons')
        indexes = [
            models.Index(fields=['full_name'], name='person_full_name_idx')
        ]


class PersonRole(models.TextChoices):
    ACTOR = 'actor', _('Actor')
    DIRECTOR = 'director', _('Director')
    WRITER = 'writer', _('Writer')
    PRODUCER = 'producer', _('Producer')


class PersonFilmWork(UUIDMixin):
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.CharField(_('role'), max_length=20, choices=PersonRole.choices)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'person_film_work'
        verbose_name = _('person film work')
        verbose_name_plural = _('person film works')
        constraints = [
            models.UniqueConstraint(fields=['film_work', 'person', 'role'], name='person_film_work_unique')
        ]
        indexes = [
            models.Index(fields=['person'], name='pfw_p_id_idx'),
            models.Index(fields=['film_work'], name='pfw_fw_id_idx'),
            models.Index(fields=['role'], name='pfw_role_idx'),
        ]
