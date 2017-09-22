from django import forms
from haystack.forms import SearchForm
from .models import AssetType, SecureAsset, MetaDocumentAsset, MetaDocumentSecureAsset, Asset
from .search_backend import CustomSearchQuerySet
from cedar_settings.models import GeneralSetting


class AssetForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AssetForm, self).__init__(*args, **kwargs)
        self.fields['asset_type'].initial = AssetType.objects.get(type_of_asset='Uncategorized')
        self.fields['file'].label = ''

    # override the save and automatically set the name attribute
    # from the file if the file has been changed:
    def save(self, commit=True):
        asset = super(AssetForm, self).save(commit=False)
        if 'file' in self.changed_data:
            name = asset.file.name
            asset.name = name
        asset.save()
        return asset

    class Meta:
        model = Asset
        # exclude = ['delete_file_with_record', 'modified']
        fields = ('file',
                  'comment',
                  'asset_type',
                  # 'name'
                  )


class SecureAssetForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SecureAssetForm, self).__init__(*args, **kwargs)
        # self.fields['asset_type'].initial = AssetType.objects.get(type_of_asset='Uncategorized')
        self.fields['file'].label = ''

    # override the save and automatically set the name attribute
    # from the file if the file has been changed:
    def save(self, commit=True):
        asset = super(SecureAssetForm, self).save(commit=False)
        if 'file' in self.changed_data:
            name = asset.file.name
            asset.name = name
        asset.save()
        return asset

    class Meta:
        model = SecureAsset
        # exclude = ['delete_file_with_record', 'modified']
        fields = ('file',
                  'comment',
                  'asset_type',
                  # 'name'
                  )


class SecureAssetSearchForm(SearchForm):

    asset_type = forms.ModelMultipleChoiceField(
        queryset=AssetType.objects.all(),
        # widget=forms.CheckboxSelectMultiple
        required=False,
        show_hidden_initial=False,
        widget=forms.SelectMultiple(attrs={'class': 'multiple'}),
        # initial={'asset_type': AssetType.objects.filter(type_of_asset='Transcript').first().id}
        initial={'asset_type': AssetType.objects.values_list('id', flat=True)},
    )

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

        super(SecureAssetSearchForm, self).__init__(*args, **kwargs)

    # Keep the below for reference. May be searching by dates at some point:
    def alternate_search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(SecureAssetSearchForm, self).search()

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

        asset_types = self.cleaned_data.get('asset_type', None)

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
        sqs = self.searchqueryset.raw_search('({})'.format(self.cleaned_data['q']))

        # set asset types if needed:
        if asset_types:
            sqs = sqs.filter(asset_type__in=asset_types)

        sqs = sqs.highlight(fragsize=fragmentsize, snippets=snippets_num)

        if self.load_all:
            sqs = sqs.load_all()

        return sqs


class MetaDocumentSecureAssetForm(forms.ModelForm):
    class Meta:
        model = MetaDocumentSecureAsset
        fields = '__all__'


class MetaDocumentAssetForm(forms.ModelForm):
    class Meta:
        model = MetaDocumentAsset
        fields = '__all__'


class FileSettingForm(AssetForm):
    setting_choices = (
        ('example', 'choice')
    )
    setting = forms.ChoiceField(choices=setting_choices, required=False, label="Setting Name")

    def __init__(self, *args, **kwargs):
        super(FileSettingForm, self).__init__(*args, **kwargs)
        # self.fields['setting'].choices = GeneralSetting.objects.all().values_list(['name', 'name'])
        self.fields['setting'].choices = [(obj.name, obj.name) for obj in GeneralSetting.objects.all()]

    def save(self, commit=True):
        instance = super(FileSettingForm, self).save(commit=True)

        setting = self.cleaned_data.get('setting', None)
        GeneralSetting.objects.set(
            name=setting,
            value=instance,
            # value = Asset.objects.first(),
            data_type='reference'
        )
        return instance

    class Meta(AssetForm.Meta):
        model = Asset
        fields = AssetForm.Meta.fields + ('setting',)
