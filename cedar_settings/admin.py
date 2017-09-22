from django.contrib import admin
from django.conf import settings

from .models import GeneralSetting


class GeneralSettingAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'data_type',
        'value'
    ]

if settings.DEBUG:
    admin.site.register(GeneralSetting, GeneralSettingAdmin)
