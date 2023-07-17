from django.contrib.auth import get_user_model
from django.contrib import admin

User = get_user_model()

admin.site.register(
    User,
    list_display=('email', 'username', 'is_active', 'is_staff'),
    list_filter=('email', 'username', 'is_superuser', 'is_staff')
)
