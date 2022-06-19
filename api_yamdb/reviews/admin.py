from django.contrib import admin

from .models import Category, Genre, Title, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'role',)
    search_fields = ('username',)
    list_filter = ('username',)
    empty_value_display = '-пусто-'


admin.site.register(Category)
# admin.site.register(Comment)
admin.site.register(Genre)
# admin.site.register(Review)
admin.site.register(Title)
admin.site.register(User, UserAdmin)
