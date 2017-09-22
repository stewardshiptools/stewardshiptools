"""
Library form classes.
Put something helpful here.
"""
from django import forms
from tags.widgets import TagAutoSuggestSelect2
from mptt.forms import TreeNodeChoiceField
from django.contrib.contenttypes.models import ContentType

from django.core.urlresolvers import reverse_lazy

from haystack.forms import SearchForm
from haystack.query import SQ, Raw

from cedar.widgets import Select2Ajax
from library.search_backend import CustomSearchQuerySet

from library.models import Item, ItemType, DublinCore, Holdings, Review, ResearcherNotes, Confidentiality, CollectionTag, \
    CaseBrief, Synthesis, SynthesisCategory, SynthesisItem, PersonMentionedTag

from security.forms import SecurityLevelModelFormMixin


class BelongsToFormMixin(object):
    """
    Draws to the belongs_to value from initial or instance (if 'update')
    """
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            self.belongs_to = instance.belongs_to
        else:
            self.belongs_to = kwargs['initial'].get('belongs_to')
        super().__init__(*args, **kwargs)


class ItemForm(SecurityLevelModelFormMixin, BelongsToFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)

        # dublin core is actually required by the DB, but the way
        # I am doing these forms is whacked
        self.fields['dublin_core'].required = False
        self.fields['tags'].required = False
        self.fields['collections'].required = False

        self.fields['related_items'].label_from_instance = lambda obj: "{} ({})".format(str(obj), obj.prefixed_id)

        # we set this widget dynamically because it needs to be instantiated with the correct belongs_to kwarg.
        self.fields['collections'].widget = TagAutoSuggestSelect2(
            tagmodel='library.CollectionTag',
            attrs={'startText': " "},
            min_input=0,
            # extra_url_params={'belongs_to': self.belongs_to}
        )

    class Meta:
        model = Item

        # Files need excluded here or else they break the .save -> .save_m2m call.
        # They can be added and handled separately.
        exclude = ('extra_data', 'related_object', 'content_type', 'object_id', 'files')

        widgets = {
            'tags': TagAutoSuggestSelect2(tagmodel='tags.Tag', attrs={'startText': " "}, min_input=0),
        }


class DublinCoreForm(forms.ModelForm):
    type = TreeNodeChoiceField(queryset=ItemType.objects.all())

    def __init__(self, *args, **kwargs):
        super(DublinCoreForm, self).__init__(*args, **kwargs)
        self.fields['type'].required = False

    class Meta:
        model = DublinCore
        fields = '__all__'


class HoldingsForm(forms.ModelForm):
    class Meta:
        model = Holdings
        fields = '__all__'


class ReviewForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['people_mentioned'].required = False
        self.fields['plants'].required = False
        self.fields['animals'].required = False


    class Meta:
        model = Review
        fields = '__all__'

        widgets = {
            'places_mentioned': Select2Ajax(ajax_url=reverse_lazy('heritage:place-suggestions'), attrs={'startText': " "}),
            'people_mentioned': TagAutoSuggestSelect2(tagmodel='library.PersonMentionedTag', attrs={'startText': " "}),
            'plants': TagAutoSuggestSelect2(tagmodel='ecosystems.PlantTag', attrs={'startText': " "},
                                            ajax_url=reverse_lazy('ecosystems:plant-suggestions'), freetagging=False),
            'animals': TagAutoSuggestSelect2(tagmodel='ecosystems.AnimalTag', attrs={'startText': " "},
                                             ajax_url=reverse_lazy('ecosystems:animal-suggestions'), freetagging=False),
        }


class ResearcherNotesForm(forms.ModelForm):
    class Meta:
        model = ResearcherNotes
        fields = '__all__'


class ConfidentialityForm(forms.ModelForm):
    class Meta:
        model = Confidentiality
        # fields = '__all__'
        exclude = ('confidential',)


class CollectionTagForm(BelongsToFormMixin, forms.ModelForm):
    """
    For editing the collection tag description field. Could be used for adding/removing linked Items.
    """
    def __init__(self, *args, **kwargs):
        super(CollectionTagForm, self).__init__(*args, **kwargs)
        self.fields['slug'].required = False

    class Meta:
        model = CollectionTag
        fields = '__all__'

    def save(self, commit=True):
        instance = super(CollectionTagForm, self).save(commit=False)
        instance.slug = instance.slugify(instance.name)
        if commit:
            instance.save()
        return instance


class CaseBriefForm(BelongsToFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # alter select choice verbose texts with this:
        self.fields['keywords'].label_from_instance = lambda obj: "{} ({})".format(str(obj), obj.prefixed_id)
        self.fields['sources'].label_from_instance = lambda obj: "{} ({})".format(str(obj), obj.prefixed_id)

        # we set this widget dynamically because it needs to be instantiated with the correct belongs_to kwarg.
        self.fields['keywords'].widget = TagAutoSuggestSelect2(
            tagmodel='library.CaseBriefTag',
            attrs={'startText': " "},
            min_input=0,
            # extra_url_params={'belongs_to': self.belongs_to}
        )

    class Meta:
        model = CaseBrief
        fields = '__all__'

        widgets = {
            'tags': TagAutoSuggestSelect2(tagmodel='tags.Tag', attrs={'startText': " "}, min_input=0),
        }

    def save(self, commit=True):
        obj = super().save(commit=commit)
        obj.save()
        return obj


class SynthesisForm(BelongsToFormMixin, forms.ModelForm):
    class Meta:
        model = Synthesis
        fields = '__all__'


class SynthesisItemForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # alter select choice verbose texts with this:
        self.fields['casebriefs'].label_from_instance = lambda obj: "{} ({})".format(str(obj), obj.prefixed_id)
        self.fields['items'].label_from_instance = lambda obj: "{} ({})".format(str(obj), obj.prefixed_id)

    class Meta:
        model = SynthesisItem
        fields = '__all__'


class PersonMentionedTagForm(forms.ModelForm):
    """
    For editing the Person mentioned tag description field. Could be used for adding/removing linked Items.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False

    class Meta:
        model = PersonMentionedTag
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = instance.slugify(instance.name)
        if commit:
            instance.save()
        return instance


class LibrarySearchForm(SearchForm):
    number_of_excerpt_characters = forms.IntegerField(initial=500, required=True, max_value=51200)
    page = forms.IntegerField(widget=forms.HiddenInput(), initial=1)  # for the paginator
    return_as_csv = forms.CharField(widget=forms.HiddenInput(), initial="no", required=False)

    def __init__(self, *args, **kwargs):

        self.searchqueryset = kwargs.pop('searchqueryset', None)
        self.load_all = kwargs.pop('load_all', False)

        # This conditional was copied out of the source but never resolves True.
        # THe type of SearchQuerySEt was overriden in the View
        # Probably dumpable.
        if self.searchqueryset is None:
            self.searchqueryset = CustomSearchQuerySet()

        kwargs['searchqueryset'] = self.searchqueryset

        # grab selected facets...
        self.facets = kwargs.pop("facets", dict())

        # Init the form!
        super().__init__(*args, **kwargs)

        # Auto create select multiple fields for each facet field.
        facet_choices = dict()
        for field, facets in self.facets.get('fields', dict()).items():
            facet_choices[field] = []
            label = field

            for value, count in facets:
                if count > 0:

                    if field == 'django_ct':
                        label = "Content type"
                        app_label, model_name = value.rsplit('.', 1)
                        ct = ContentType.objects.get_by_natural_key(app_label, model_name)

                        facet_choices[field].append((value, "{} ({})".format(ct.name.title(), count)))
                    elif field == 'date':
                        facet_choices[field].append((value, "{} ({})".format(str(value).split("T")[0], count)))
                    else:
                        facet_choices[field].append((value, "{} ({})".format(value, count)))

            if facet_choices[field]:
                self.fields["{}_facet".format(field)] = forms.MultipleChoiceField(
                    label=label.replace('_', ' ').title(),
                    required=False,
                    choices=sorted(facet_choices[field])
                )

    # Keep the below for reference. May be searching by dates at some point:
    def alternate_search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super().search()

        if not self.is_valid():
            return self.no_query_found()

            # # Check to see if a start_date was chosen.
            # if self.cleaned_data['start_date']:
            #     sqs = sqs.filter(pub_date__gte=self.cleaned_data['start_date'])
            #
            # # Check to see if an end_date was chosen.
            # if self.cleaned_data['end_date']:
            #     sqs = sqs.filter(pub_date__lte=self.cleaned_data['end_date'])

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get('q'):
            return self.no_query_found()

        fragmentsize = self.cleaned_data.get('number_of_excerpt_characters', 500)

        # Hardcode max number of snippets here to 100. The backend has set the maximum
        # possible number of characters analyzed to 1 million, so, snippets_num
        # could potentially be bumped up a lot higher, doesn't seem very useful to
        # me though.
        snippets_num = 100

        # The haystack sqs filtering is not adding the asset_type portion of the
        # query properly -> it is no wrapping it in () as it needs to.
        # UPDATE: solr has a weird interpretation of AND/OR precedence.
        # see: http://robotlibrarian.billdueber.com/2011/12/solr-and-boolean-operators/
        # We should seriously consider dropping the AND/OR syntax and using the
        # Google-like EDISMAX query parser.
        # sqs = self.searchqueryset.raw_search(self.cleaned_data['q']) \
        #     .filter(asset_type__in=asset_types) \
        #     .highlight(fragsize=fragmentsize, snippets=snippets_num)


        # Manually wrap the query with parentheses and life goes on....
        # sqs = self.searchqueryset.raw_search('({})'.format(self.cleaned_data['q']))
        q = self.cleaned_data['q']
        sqs = self.searchqueryset.filter(SQ(text=Raw('({})'.format(q))) | SQ(name=Raw('({})'.format(q))))

        # Narrow the search by applied facets before applying raw queries.
        #
        # We need to process each facet to ensure that the field name and the
        # value are quoted correctly and separately:
        facet_query = SQ()
        if self.facets.get('fields'):
            for field, facets in self.facets['fields'].items():
                selected_facets = self.cleaned_data.get("{}_facet".format(field), [])

                facet_subquery = SQ()  # OR the individual facet queries.
                # OR the facet subqueries on to eachother for this field.
                for facet_value in selected_facets:
                    facet_subquery.add(SQ(**{field: Raw('"{}"'.format(sqs.query.clean(facet_value)))}), SQ.OR)

                # AND the field facet query to the main filter
                if facet_subquery.children:
                    facet_query.add(facet_subquery, SQ.AND)

            if facet_query.children:
                sqs = sqs.filter(facet_query)

        sqs = sqs.highlight(fragsize=fragmentsize, snippets=snippets_num)

        if self.load_all:
            sqs = sqs.load_all()

        return sqs
