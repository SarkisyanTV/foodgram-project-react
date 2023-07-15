from django.contrib.auth import get_user_model
from django.contrib import admin

User = get_user_model()

admin.site.register(
    User,
    filter='email',
    list_display=('email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff'),
    list_filter=('is_active', 'is_superuser', 'is_staff')
)
