from django.contrib import admin

from actions.models import ActionMaster, Action


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    pass
