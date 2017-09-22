from django.contrib import admin

from tags.models import Tag, TaggedItem


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(TaggedItem)
class TagAdmin(admin.ModelAdmin):
    pass
