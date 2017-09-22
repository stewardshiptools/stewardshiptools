from django.contrib import admin
from security.models import SecurityLevel


@admin.register(SecurityLevel)
class SecurityLevelAdmin(admin.ModelAdmin):
    list_display = ('obj', 'level')
