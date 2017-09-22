from haystack.backends.solr_backend import SolrSearchBackend, SolrSearchQuery, SolrEngine
from haystack.query import SearchQuerySet


#####################################################
# Hay-hacked Solr Backend:
#####################################################


# Made this for reference.
class CustomSearchQuerySet(SearchQuerySet):

    def raw_search(self, query_string, **kwargs):
        """Passes a raw query directly to the backend."""
        qs = super(CustomSearchQuerySet, self).raw_search(query_string, **kwargs)
        # return self.filter(content=Raw(query_string, **kwargs))
        return qs

    def highlight(self, fragsize=500, snippets=100, require_field_match=True):
        """Adds highlighting to the results."""
        clone = self._clone()
        rmf = 'true' if require_field_match else 'false'
        clone.query.add_highlight(str(fragsize), str(snippets), rmf)
        return clone


class CustomSolrSearchQuery(SolrSearchQuery):
    highlight = False
    highlight_fragsize = '500'
    highlight_snippets = '100'
    highlight_require_field_match = 'true'
    highlight_max_analyzed_chars = 1000000  # override solr default of 512000. Not accepted as a add_highlight parameter.

    # hl.maxAnalyzedChars   -> solr default is 51200. I have not implemented this so default stands.
    # make form set max frag size to this value.

    def add_highlight(self, fragsize, snippets, require_field_match):
        super(CustomSolrSearchQuery, self).add_highlight()  # Sets self.highlight = True
        self.highlight_fragsize = fragsize
        self.highlight_snippets = snippets
        self.highlight_require_field_match = require_field_match

    def build_params(self, spelling_query=None, **kwargs):
        search_kwargs = super(CustomSolrSearchQuery, self).build_params(spelling_query=spelling_query, kwargs=kwargs)

        if self.highlight is True:
            search_kwargs['highlight'] = self.highlight
            search_kwargs['hl.fragsize'] = self.highlight_fragsize
            search_kwargs['hl.snippets'] = self.highlight_snippets
            search_kwargs['hl.requireFieldMatch'] = self.highlight_require_field_match
            search_kwargs['hl.maxAnalyzedChars'] = self.highlight_max_analyzed_chars

        return search_kwargs


# Override the search backend so we can play with the fragment sizes without messing
# up the solr backend class. Re-wrote build_search_kwgards to ACCEPT kwargs instead
# of positional arguments so that we can supply additional args as we need.
# see: https://wiki.apache.org/solr/HighlightingParameters#hl.fragsize
class CustomSolrSearchBackend(SolrSearchBackend):
    def build_search_kwargs(self, query_string, **search_kwargs):

        sort_by = search_kwargs.pop('sort_by', None)
        start_offset = search_kwargs.pop('start_offset', 0)
        end_offset = search_kwargs.pop('end_offset', None)
        fields = search_kwargs.pop('fields', '')
        highlight = search_kwargs.pop('highlight', False)
        facets = search_kwargs.pop('facets', None)
        date_facets = search_kwargs.pop('date_facets', None)
        query_facets = search_kwargs.pop('query_facets', None)
        narrow_queries = search_kwargs.pop('narrow_queries', None)
        spelling_query = search_kwargs.pop('spelling_query', None)
        within = search_kwargs.pop('within', None)
        dwithin = search_kwargs.pop('dwithin', None)
        distance_point = search_kwargs.pop('distance_point', None)
        models = search_kwargs.pop('models', None)
        limit_to_registered_models = search_kwargs.pop('limit_to_registered_models', None)
        result_class = search_kwargs.pop('result_class', None)
        stats = search_kwargs.pop('stats', None)

        super_search_kwargs = super(CustomSolrSearchBackend, self).build_search_kwargs(
            query_string, sort_by, start_offset, end_offset,
            fields, highlight, facets,
            date_facets, query_facets,
            narrow_queries, spelling_query,
            within, dwithin, distance_point,
            models, limit_to_registered_models,
            result_class, stats
        )

        # Augment the search kwargs with our own here:
        if highlight is True:
            super_search_kwargs['hl'] = 'true'

            fragsize = search_kwargs.pop('hl.fragsize', None)
            if fragsize:
                super_search_kwargs['hl.fragsize'] = fragsize

            snippets = search_kwargs.pop('hl.snippets', None)
            if snippets:
                super_search_kwargs['hl.snippets'] = snippets

            require_field_match = search_kwargs.pop('hl.requireFieldMatch', None)
            if require_field_match:
                super_search_kwargs['hl.requireFieldMatch'] = require_field_match

            max_analyzed_chars = search_kwargs.pop('hl.maxAnalyzedChars', None)
            if max_analyzed_chars:
                super_search_kwargs['hl.maxAnalyzedChars'] = max_analyzed_chars

        return super_search_kwargs


# Extend the Engine class so we can implement our own back end class, so that we can mess with fragment sizes (at least for now).
class CustomSolrEngine(SolrEngine):
    backend = CustomSolrSearchBackend
    query = CustomSolrSearchQuery
