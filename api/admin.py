from django.contrib import admin

from .models import Category, Genre, Title, Review, Comment, User


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = 'Категория не выбрана',
    prepopulated_fields = {"slug": ("name",)}


class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = 'Жанр не выбран',
    prepopulated_fields = {"slug": ("name",)}


class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'description',)
    search_fields = ('name',)
    list_filter = ('name', 'year',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title_id', 'text')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'review_id', 'text')


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'REQUIRED_FIELDS', 'role')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(User, UserAdmin)
