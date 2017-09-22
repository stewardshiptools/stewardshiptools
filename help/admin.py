from django.contrib import admin
from django.core import urlresolvers
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from . import models


class PageHelpAdmin(admin.ModelAdmin):
    list_display = ['page_name', 'tooltip', 'help_texts']
    ordering = ('page_name',)
    filter_horizontal = ("help_text",)

    # Linkify the help text titles:
    def help_texts(self, obj):
        return format_html_join(
            mark_safe(", "),
            "<a href='{}'>{}</a>",
            ((urlresolvers.reverse('admin:help_helptext_change', args=(h.id,)), h.title) for h in obj.help_text.all().order_by('title'))
        )

    help_texts.allow_tags = True


class HelpTextAdmin(admin.ModelAdmin):
    list_display = ['title', 'assigned_to']
    ordering = ('title',)
    search_fields = ['html', ]

    # Linkify the help text assignments:
    def assigned_to(self, obj):
        return format_html_join(
            mark_safe(", "),
            "<a href='{}'>{}</a>",
            ((urlresolvers.reverse('admin:help_pagehelp_change', args=(pg.id,)), pg.page_name) for pg in obj.pagehelp_set.all().order_by('page_name'))
        )

        assigned_to.allow_tags = True


# Register your models here.
admin.site.register(models.PageHelp, PageHelpAdmin)
admin.site.register(models.HelpText, HelpTextAdmin)
