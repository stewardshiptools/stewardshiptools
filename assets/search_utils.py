from unidecode import unidecode

from haystack.utils import Highlighter
from haystack import connection_router, connections
from haystack.exceptions import NotHandled

from django.utils.html import strip_tags
from django.utils.encoding import force_text
from django.utils import six
import math


# TODO: Write custom search view (not here!) that disallows search terms that are sensitive.
# TODO: Make it so textblocks2 returns something closer to the max_length - returns 2*max_length right now.


def remove_asset_from_index_signal_method(sender, asset_instance):
    """
    remove_asset_from_index_signal_method: Takes an instance of :model: `assets.SecureAsset' and tries to
    remove it from the index.
    :param sender:
    :param asset_instance: an instance of an asset model
    :return: none
    """

    # NOTE: this code blatantly ripped off haystack source files.
    using_backends = connection_router.for_write(instance=asset_instance)

    for using in using_backends:
        try:
            index = connections[using].get_unified_index().get_index(sender)
            index.remove_object(asset_instance, using=using)
            # print("object successfully removed from index:", instance)
        except NotHandled as e:
            # print(e, ": could not remove object from index:", asset_instance)
            pass


def update_asset_index_signal_method(sender, asset_instance):
    """
    update_asset_index_signal_method: Takes an instance of :model: `assets.SecureAsset' and tries to
    update it's index data. This method is left here as reference and is not used...yet.
    :param sender:
    :param asset_instance: an instance of an asset model
    :return: none
    """

    # NOTE: this code blatantly ripped off haystack source files.
    using_backends = connection_router.for_write(instance=asset_instance)

    for using in using_backends:
        try:
            index = connections[using].get_unified_index().get_index(sender)
            index.update_object(asset_instance, using=using)
        except NotHandled:
            # TODO: Maybe log it or let the exception bubble?
            pass


# This class is now unused:
class DocumentTextHighlighter(Highlighter):
    # Override the whole init so we can redo the query_words...
    def __init__(self, query, **kwargs):
        super(DocumentTextHighlighter, self).__init__(query, **kwargs)
        # self.query = query
        # self.query_words = set([word.lower() for word in self.query.split() if not word.startswith('-')])
        self.query_words = parse_query_terms(self.query)

    def find_window(self, highlight_locations):
        # their start puts the highlighted term at the beginning.
        their_start, their_end = super(DocumentTextHighlighter, self).find_window(highlight_locations)
        if self.max_length:
            new_start = their_start - self.max_length / 2
            new_start = 0 if new_start < 0 else new_start

            new_end = new_start + self.max_length
            new_end = len(self.text_block) - 1 if new_end > len(self.text_block) else new_end

            return int(new_start), int(new_end)
        else:
            return their_start, their_end

    def find_highlightable_words(self):
        # Use a set so we only do this once per unique word.
        word_positions = {}

        # Pre-compute the length.
        end_offset = len(self.text_block)
        lower_text_block = self.text_block.lower()

        for word in self.query_words:
            if not word in word_positions:
                word_positions[word] = []

            start_offset = 0

            while start_offset < end_offset:
                next_offset = lower_text_block.find(word.lower(), start_offset, end_offset)

                # If we get a -1 out of find, it wasn't found. Bomb out and
                # start the next word.
                if next_offset == -1:
                    break

                word_positions[word].append(next_offset)
                start_offset = next_offset + len(word)

        return word_positions

    # def highlight(self, text_block):
    #     # Could do some stuff here, but just call the super:
    #     return super(DocumentTextHighlighter, self).highlight(text_block)

    def render_html(self, highlight_locations=None, start_offset=None, end_offset=None):
        # Start by chopping the block down to the proper window.
        text = self.text_block[start_offset:end_offset]

        # Invert highlight_locations to a location -> term list
        term_list = []

        for term, locations in highlight_locations.items():
            term_list += [(loc - start_offset, term) for loc in locations]

        loc_to_term = sorted(term_list)

        # Prepare the highlight template
        if self.css_class:
            hl_start = '<%s class="%s">' % (self.html_tag, self.css_class)
        else:
            hl_start = '<%s>' % (self.html_tag)

        hl_end = '</%s>' % self.html_tag

        # Copy the part from the start of the string to the first match,
        # and there replace the match with a highlighted version.
        highlighted_chunk = ""
        matched_so_far = 0
        prev = 0
        prev_str = ""

        for cur, cur_str in loc_to_term:
            # This can be in a different case than cur_str
            actual_term = text[cur:cur + len(cur_str)]

            # Handle incorrect highlight_locations by first checking for the term ==== DISABLED!!!!!
            # if actual_term.lower() == cur_str:
            #     if cur < prev + len(prev_str):
            #         continue

            highlighted_chunk += text[prev + len(prev_str):cur] + hl_start + actual_term + hl_end
            prev = cur
            prev_str = cur_str

            # Keep track of how far we've copied so far, for the last step
            matched_so_far = cur + len(actual_term)

        # Don't forget the chunk after the last term
        highlighted_chunk += text[matched_so_far:]

        if start_offset > 0:
            highlighted_chunk = '...%s' % highlighted_chunk

        if end_offset < len(self.text_block):
            highlighted_chunk = '%s...' % highlighted_chunk

        return highlighted_chunk



    # Returns one text block per search word occurrence.
    def text_blocks(self, text):
        self.text_block = strip_tags(text)
        text_blocks = []
        word_locations = self.find_highlightable_words()
        for word in word_locations:
            for location in word_locations[word]:
                temp_location_dict = {word: [location]}  # Use this to fool the find window method.
                start_offset, end_offset = self.find_window(temp_location_dict)
                new_block = text[start_offset: end_offset]
                text_blocks.append(new_block)
        return text_blocks

    # Groups text blocks to reduce duplication.
    # Setting self.max_length is required for this to work.
    # Note that due to binning and padding on each bin, the
    # resulting length of each text block can be DOUBLE the max_length.
    def text_blocks2(self, text):
        self.text_block = strip_tags(text)
        text_blocks = []

        word_locations = self.find_highlightable_words()

        # Get flat list of all word locations:
        location_list = []
        for word in word_locations:
            location_list.extend(word_locations[word])

        if len(location_list) == 0:
            print("Error building text block! \"{}\" were/was not found in text but a"
                  " document was still returned.".format(",".join(word_locations.keys())))
            return [
                'Search term(s) {}, not found in text.'.format(",".join(word_locations.keys())),
                text
            ]

        # Remove any dupes:
        location_list = set(location_list)

        # Decide how many groups
        minimum = min(location_list)
        maximum = max(location_list)
        location_range = max(location_list) - minimum
        num_groups = math.ceil(location_range / self.max_length)
        num_groups = 1 if num_groups == 0 else num_groups  # Make sure there's always at least one group.
        bins = []

        bin_start = minimum
        for x in range(num_groups):
            bin_end = bin_start + self.max_length
            if bin_end > len(self.text_block):
                bin_end = len(self.text_block)

            bins.append([bin_start, bin_end])
            bin_start += self.max_length

        # Make sure each bin actually contains a word location
        # because we only used simple min/max to get # of bins:
        bins_to_keep = []
        for i in range(len(bins)):
            word_bin = bins[i]
            has_word = False
            for location in location_list:
                if location >= word_bin[0] and location <= word_bin[1]:
                    has_word = True
                    break

            if has_word:
                bins_to_keep.append(word_bin)

        bins = bins_to_keep

        # Add a little padding to the start and end of each group,
        # this can create some overlap between groups... meh.
        for i in range(len(bins)):
            bin_start = bins[i][0]
            bin_end = bins[i][1]

            bin_start -= int(self.max_length / 2)
            bin_start = 0 if bin_start < 0 else bin_start

            bin_end += int(self.max_length / 2)
            bin_end = len(self.text_block) if bin_end > len(self.text_block) else bin_end

            bins[i][0] = bin_start
            bins[i][1] = bin_end

        for word_bin in bins:
            text_blocks.append(self.text_block[word_bin[0]:word_bin[1]])

        return text_blocks


# DEPRECATED: This older subtexter will use either the solr OR the previous hacked subtexting functions.
# It's a little misleading so better to use the other "get_subtexts" function below.
def get_subtexts_old(search_list, context_query):
    # Use the highlighter to build text chunks of size "max_length"
    hl = DocumentTextHighlighter(context_query, max_length=200)

    subtexts = {}  # Keys are SearchResult PKs, values are lists of texts.
    for document in search_list:
        if document.highlighted:
            subtexts[document.pk] = document.highlighted['text']
        else:
            subtexts[document.pk] = hl.text_blocks2(document.text)
        # hl_words = hl.find_highlightable_words()

    return subtexts


# Returns subtexts created by solr, or "" if one isn't found.
def get_subtexts(search_list):
    subtexts = {}  # Keys are SearchResult PKs, values are lists of texts.
    for document in search_list:
        if document.highlighted:
            subtexts[document.pk] = []
            for snippet in document.highlighted['text']:
                subtexts[document.pk].append(clean_weird_chars(snippet))
        else:
            subtexts[document.pk] = ''
    return subtexts


def parse_query_terms(querystring):
    """
    Parses tag input, with multiple word input being activated and
    delineated by commas and double quotes. Quotes take precedence, so
    they may contain commas.
    Returns a sorted list of unique tag names.
    Ported from Jonathan Buchanan's `django-tagging
    <http://django-tagging.googlecode.com/>`_
    Ported from django-taggit:
    https://github.com/alex/django-taggit/blob/develop/taggit/utils.py

    Note:
        I had to use this earlier to re-determine the search terms enterend
        by the user. This should not be used if the solr <em> tags are being used...I hope.
    """
    if not querystring:
        return []

    querystring = force_text(querystring)

    # Special case - if there are no commas or double quotes in the
    # input, we don't *do* a recall... I mean, we know we only need to
    # split on spaces.
    if ',' not in querystring and '"' not in querystring:
        words = list(set(split_strip(querystring, ' ')))
        words.sort()
        return words

    words = []
    buffer = []
    # Defer splitting of non-quoted sections until we know if there are
    # any unquoted commas.
    to_be_split = []
    saw_loose_comma = False
    open_quote = False
    i = iter(querystring)
    try:
        while True:
            c = six.next(i)
            if c == '"':
                if buffer:
                    to_be_split.append(''.join(buffer))
                    buffer = []
                # Find the matching quote
                open_quote = True
                c = six.next(i)
                while c != '"':
                    buffer.append(c)
                    c = six.next(i)
                if buffer:
                    word = ''.join(buffer).strip()
                    if word:
                        words.append(word)
                    buffer = []
                open_quote = False
            else:
                if not saw_loose_comma and c == ',':
                    saw_loose_comma = True
                buffer.append(c)
    except StopIteration:
        # If we were parsing an open quote which was never closed treat
        # the buffer as unquoted.
        if buffer:
            if open_quote and ',' in buffer:
                saw_loose_comma = True
            to_be_split.append(''.join(buffer))
    if to_be_split:
        if saw_loose_comma:
            delimiter = ','
        else:
            delimiter = ' '
        for chunk in to_be_split:
            words.extend(split_strip(chunk, delimiter))
    words = list(set(words))
    words.sort()
    return words


def split_strip(string, delimiter=','):
    """
    Splits ``string`` on ``delimiter``, stripping each resulting string
    and returning a list of non-empty strings.
    Ported from Jonathan Buchanan's `django-tagging
    <http://django-tagging.googlecode.com/>`_
    Ported from django-taggit:
    https://github.com/alex/django-taggit/blob/develop/taggit/utils.py

    Note:
        I had to use this earlier to re-determine the search terms enterend
        by the user. This should not be used if the solr <em> tags are being used...I hope.
    """
    if not string:
        return []

    words = [w.strip() for w in string.split(delimiter)]
    return [w for w in words if w]


def clean_weird_chars(string):
    clean = ""
    for s in string:
        clean += unidecode(s)
    return clean
