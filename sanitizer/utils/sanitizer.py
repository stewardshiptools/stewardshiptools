"""
:file: sanitizer.py

Contains the main utility functions actually related to sanitizing text.
"""
import re

from django.contrib.contenttypes.models import ContentType

from sanitizer.models import SensitivePhrase, RelatedSensitivePhrase


def get_relevant_phrases(obj=None):
    """ Get all phrases to be searched for.  This includes all SensitivePhrases, and any RelatedSensitivePhrases that
    refer to the given object.

    :param obj: A model instance to check for sensitive phrases made specifically for that instance.
    :return: a dictionary of replacement phrases keyed by the phrases being replaced.
    """
    replacements = []

    content_type = ContentType.objects.get_for_model(obj)
    related_sensitive_phrases = RelatedSensitivePhrase.objects.filter(
        content_type__pk=content_type.id,
        object_id=obj.id
    ).extra(select={'length': 'Length(phrase)'}).order_by('-length', 'phrase')

    for phrase in related_sensitive_phrases:
        replacements.append({
            'phrase': phrase.phrase,
            'replacement': phrase.replace_phrase,
            'start_boundary': phrase.check_for_word_boundary_start,
            'end_boundary': phrase.check_for_word_boundary_end
        })

    sensitive_phrases = SensitivePhrase.objects.all() \
        .extra(select={'length': 'Length(phrase)'}).order_by('-length', 'phrase')

    for phrase in sensitive_phrases:
        replacements.append({
            'phrase': phrase.phrase,
            'replacement': phrase.replace_phrase,
            'start_boundary': phrase.check_for_word_boundary_start,
            'end_boundary': phrase.check_for_word_boundary_end
        })

    return replacements


def sanitize(text, replace_char='_', obj=None):
    phrase_replacements = get_relevant_phrases(obj)
    replacements = 0

    for r in phrase_replacements:
        phrase = r['phrase']
        replacement = r['replacement']
        if not replacement:
            replacement = replace_char * len(phrase)

        if r['start_boundary']:
            start_boundary = r"(?P<boundarya>\b|_)"
            start_boundary_repl = "\g<boundarya>"
        else:
            start_boundary = ""
            start_boundary_repl = ""
        if r['end_boundary']:
            end_boundary = r"(?P<boundaryb>\b|_)"
            end_boundary_repl = "\g<boundaryb>"
        else:
            end_boundary = ""
            end_boundary_repl = ""

        pattern = r"%s%s%s" % (start_boundary, phrase, end_boundary)

        text, num_replacements = re.subn(pattern, r"%s%s%s" % (start_boundary_repl, replacement, end_boundary_repl),
                                         text, flags=re.I)
        text, num_replacements = re.subn(pattern, r"%s%s%s" % (start_boundary_repl, replacement, end_boundary_repl),
                                         text, flags=re.I)
        replacements += num_replacements

    return text
