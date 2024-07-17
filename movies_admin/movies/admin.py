from django.contrib import admin
from .models import Genre,FilmWork,GenreFilmwork,Person


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass

class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


@admin.register(FilmWork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline,)
    list_display=("title","type","creation_date","rating")
    list_filter = ('type',)
    search_fields = ('title', 'description', 'id')
@admin.register(GenreFilmwork)
class GenreAdmin(admin.ModelAdmin):
    pass
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display=("full_name",)
