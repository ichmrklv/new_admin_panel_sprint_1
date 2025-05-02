from django.contrib import admin
from .models import Genre, FilmWork, GenreFilmWork, Person, PersonFilmWork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created', 'modified',)  
    search_fields = ('name',) 
    list_filter = ('name',) 
    

class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmWorkInline, PersonFilmWorkInline,)

    list_display = ('title', 'description', 'creation_date', 'rating', 'type', 'created', 'modified',)
    list_filter = ('type',)
    search_fields = ('title', 'description', 'id') 


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork
    extra = 1
    autocomplete_fields = ['film_work']
    fields = ('film_work', 'role')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'created', 'modified')
    search_fields = ('full_name',)
    list_filter = ('created',)
    inlines = [PersonFilmWorkInline] 


