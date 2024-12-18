from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils.html import format_html

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ('username', 'email', 'profile_photo_tag', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'profile_photo')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'profile_photo', 'is_staff', 'is_active'),
        }),
    )

    filter_horizontal = ()

    search_fields = ('username', 'email')
    ordering = ('username',)

    def profile_photo_tag(self, obj):
        if obj.profile_photo:
            return format_html(f'<img src="{obj.profile_photo.url}" style="width: 50px; height: 50px; border-radius: 25px;" />')
        return "No Image"
    profile_photo_tag.short_description = 'Profile Photo'
