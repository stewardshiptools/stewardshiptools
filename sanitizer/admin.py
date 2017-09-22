from django.contrib import admin
from sanitizer.models import SensitivePhrase, RelatedSensitivePhrase


@admin.register(SensitivePhrase)
class SensitivePhraseAdmin(admin.ModelAdmin):
    list_display = ['phrase', 'replace_phrase']


class RelatedSensitivePhraseInline(admin.TabularInline):
    model = RelatedSensitivePhrase


@admin.register(RelatedSensitivePhrase)
class RelatedSensitivePhraseAdmin(admin.ModelAdmin):
    list_display = ['phrase', 'replace_phrase', 'obj', 'content_type']
    search_fields = ['phrase', 'replace_phrase']
    list_filter = ['content_type']
