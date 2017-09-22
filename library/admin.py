from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from .models import Item, DublinCore, Holdings, ResearcherNotes, Review, ItemType, ItemAssetRelation, CollectionTag, CollectionTaggedItem, \
     MUPCategory, UseAndOccupancyCategory, CaseBrief, CaseBriefTag, CaseBriefTaggedItem, Synthesis, SynthesisItem, SynthesisCategory, \
    PersonMentionedTag, PersonMentionedTaggedItem


class ItemAdmin(admin.ModelAdmin):
    ordering = ('-modified',)
    list_filter = ('belongs_to',)
    search_fields = ('name',)


admin.site.register(Item, ItemAdmin)
admin.site.register(DublinCore)
admin.site.register(Holdings)
admin.site.register(ResearcherNotes)
admin.site.register(Review)
admin.site.register(ItemType, MPTTModelAdmin)
admin.site.register(ItemAssetRelation)
admin.site.register(CollectionTag)
admin.site.register(CollectionTaggedItem)
admin.site.register(MUPCategory)
admin.site.register(UseAndOccupancyCategory)
admin.site.register(CaseBrief)
admin.site.register(CaseBriefTag)
admin.site.register(CaseBriefTaggedItem)
admin.site.register(Synthesis)
admin.site.register(SynthesisItem)
admin.site.register(SynthesisCategory)
admin.site.register(PersonMentionedTag)
admin.site.register(PersonMentionedTaggedItem)
