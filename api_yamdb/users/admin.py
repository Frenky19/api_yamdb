from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Настройка отображения пользователя в административной панели."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_active',
        'date_joined',
    )
    search_fields = ('username', 'email',)
    list_filter = ('role', 'is_active', 'date_joined',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {
            'fields': ('email', 'first_name', 'last_name', 'bio')
        }),
        ('Права доступа', {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Подтверждение аккаунта', {
            'fields': ('confirmation_code',),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('username',)
    list_per_page = 20
