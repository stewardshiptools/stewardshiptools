from django.contrib.contenttypes.models import ContentType

from sanitizer.models import RelatedSensitivePhrase


# Run this if you need to build it all: python manage.py sanitize_interviews --overwrite


def interview_populate_sensitive_phrases(interview):
    participants = interview.participants.all()
    attendees = interview.attendees.all()
    num_phrases = 0

    interview_content_type = ContentType.objects.get_for_model(interview)

    participant_counter = 1
    for person in participants:
        count = create_person_related_sensitive_phrases(interview, interview_content_type, person,
                                                        'Interviewee %d' % participant_counter)
        participant_counter += 1
        num_phrases += count

    attendee_counter = 1
    for person in attendees:
        if not participants.filter(id=person.id).exists():
            count = create_person_related_sensitive_phrases(interview, interview_content_type, person,
                                                            'Attendee %d' % attendee_counter)
            attendee_counter += 1
            num_phrases += count

    return num_phrases  # Return the number of phrases processed.


def create_person_related_sensitive_phrases(obj, content_type, person, replace_phrase):
    num_phrases = 0

    # Start preparing phrases to check for and remove
    # Redact initials
    # Redact names - 5 variations
    #     "Lname, Fname"
    #     "Lname, Fname Suffix"
    #     "Fname Lname"
    #     "FnameLname"
    #     "Fname"
    #     "Lname"
    #     "Fname Lname Suffix"
    #     "FnameLnameSuffix"
    #     "Fname Suffix"
    #     "FnameSuffix"
    #     "Lname Suffix"
    #     "LnameSuffix"
    #     "IndigenousName"

    # Initials
    if not RelatedSensitivePhrase.objects.filter(
            content_type__pk=content_type.id,
            object_id=obj.id,
            phrase=person.initials,
    ).exists() and person.initials:
        if check_interview_for_conflicts(obj, person.initials, '%s', ['initials']):
            repl = '_'
        else:
            repl = replace_phrase

        RelatedSensitivePhrase.objects.create(
            obj=obj,
            phrase=person.initials,
            replace_phrase=repl
        )
        num_phrases += 1

    # Names with the suffix
    if not RelatedSensitivePhrase.objects.filter(
            content_type__pk=content_type.id,
            object_id=obj.id,
            phrase="%s,?\s*%s\s*%s" % (person.name_last, person.name_first, person.name_suffix),
            check_for_word_boundary_end=False
    ).exists() and person.name_first and person.name_last and person.name_suffix:
        if check_interview_for_conflicts(
                obj,
                "%s,?\s*%s\s*%s" % (person.name_last, person.name_first, person.name_suffix),
                "%s,?\s*%s\s*%s",
                ['name_last', 'name_first', 'name_suffix']
        ):
            repl = '_'
        else:
            repl = replace_phrase

        RelatedSensitivePhrase.objects.create(
            obj=obj,
            phrase="%s,?\s*%s\s*%s" % (person.name_last, person.name_first, person.name_suffix),
            replace_phrase=repl,
            check_for_word_boundary_end=False
        )
        num_phrases += 1

    if not RelatedSensitivePhrase.objects.filter(
            content_type__pk=content_type.id,
            object_id=obj.id,
            phrase="%s\s*%s\s*%s" % (person.name_first, person.name_last, person.name_suffix),
            check_for_word_boundary_end=False
    ).exists() and person.name_first and person.name_last and person.name_suffix:
        if check_interview_for_conflicts(
                obj,
                "%s\s*%s\s*%s" % (person.name_first, person.name_last, person.name_suffix),
                "%s\s*%s\s*%s",
                ['name_first', 'name_last', 'name_suffix']
        ):
            repl = '_'
        else:
            repl = replace_phrase

        RelatedSensitivePhrase.objects.create(
            obj=obj,
            phrase="%s\s*%s\s*%s" % (person.name_first, person.name_last, person.name_suffix),
            replace_phrase=repl,
            check_for_word_boundary_end=False
        )
        num_phrases += 1

    if not RelatedSensitivePhrase.objects.filter(
            content_type__pk=content_type.id,
            object_id=obj.id,
            phrase="%s\s*%s" % (person.name_first, person.name_suffix),
            check_for_word_boundary_end=False
    ).exists() and person.name_first:
        if check_interview_for_conflicts(
                obj,
                "%s\s*%s" % (person.name_first, person.name_suffix),
                "%s\s*%s",
                ['name_first', 'name_suffix']
        ):
            repl = '_'
        else:
            repl = replace_phrase

        RelatedSensitivePhrase.objects.create(
            obj=obj,
            phrase="%s\s*%s" % (person.name_first, person.name_suffix),
            replace_phrase=repl,
            check_for_word_boundary_end=False
        )
        num_phrases += 1

    if not RelatedSensitivePhrase.objects.filter(
            content_type__pk=content_type.id,
            object_id=obj.id,
            phrase="%s\s*%s" % (person.name_last, person.name_suffix),
            check_for_word_boundary_end=False
    ).exists() and person.name_last:
        if check_interview_for_conflicts(
                obj,
                "%s\s*%s" % (person.name_last, person.name_suffix),
                "%s\s*%s",
                ['name_last', 'name_suffix']
        ):
            repl = '_'
        else:
            repl = replace_phrase

        RelatedSensitivePhrase.objects.create(
            obj=obj,
            phrase="%s\s*%s" % (person.name_last, person.name_suffix),
            replace_phrase=repl,
            check_for_word_boundary_end=False
        )
        num_phrases += 1

    # Names without the suffix
    if not RelatedSensitivePhrase.objects.filter(
            content_type__pk=content_type.id,
            object_id=obj.id,
            phrase="%s,?\s*%s" % (person.name_last, person.name_first)
    ).exists() and person.name_first and person.name_last:
        if check_interview_for_conflicts(
                obj,
                "%s,?\s*%s" % (person.name_last, person.name_first),
                "%s,?\s*%s",
                ['name_last', 'name_first']
        ):
            repl = '_'
        else:
            repl = replace_phrase

        RelatedSensitivePhrase.objects.create(
            obj=obj,
            phrase="%s,?\s*%s" % (person.name_last, person.name_first),
            replace_phrase=repl
        )
        num_phrases += 1

    if not RelatedSensitivePhrase.objects.filter(
            content_type__pk=content_type.id,
            object_id=obj.id,
            phrase="%s\s*%s" % (person.name_first, person.name_last)
    ).exists() and person.name_first and person.name_last:
        if check_interview_for_conflicts(
                obj,
                "%s\s*%s" % (person.name_first, person.name_last),
                "%s\s*%s",
                ['name_first', 'name_last']
        ):
            repl = '_'
        else:
            repl = replace_phrase

        RelatedSensitivePhrase.objects.create(
            obj=obj,
            phrase="%s\s*%s" % (person.name_first, person.name_last),
            replace_phrase=repl
        )
        num_phrases += 1

    if not RelatedSensitivePhrase.objects.filter(
            content_type__pk=content_type.id,
            object_id=obj.id,
            phrase=person.name_first
    ).exists() and person.name_first:
        if check_interview_for_conflicts(
                obj,
                person.name_first,
                "%s",
                ['name_first']
        ):
            repl = '_'
        else:
            repl = replace_phrase

        RelatedSensitivePhrase.objects.create(
            obj=obj,
            phrase=person.name_first,
            replace_phrase=repl
        )
        num_phrases += 1

    if not RelatedSensitivePhrase.objects.filter(
            content_type__pk=content_type.id,
            object_id=obj.id,
            phrase=person.name_last
    ).exists() and person.name_last:
        if check_interview_for_conflicts(
                obj,
                person.name_last,
                "%s",
                ['name_last']
        ):
            repl = '_'
        else:
            repl = replace_phrase

        RelatedSensitivePhrase.objects.create(
            obj=obj,
            phrase=person.name_last,
            replace_phrase=repl
        )
        num_phrases += 1

    # Indigenous name
    if not RelatedSensitivePhrase.objects.filter(
            content_type__pk=content_type.id,
            object_id=obj.id,
            phrase=person.indigenous_name,
    ).exists() and person.indigenous_name:
        if check_interview_for_conflicts(
                obj,
                person.indigenous_name,
                "%s",
                ['indigenous_name']
        ):
            repl = '_'
        else:
            repl = replace_phrase

        RelatedSensitivePhrase.objects.create(
            obj=obj,
            phrase=person.indigenous_name,
            replace_phrase=repl
        )
        num_phrases += 1

    # Next get any alternate names and create entries for them...
    alternate_names = person.alternatename_set.all()
    for alternate_name in alternate_names:
        parts = alternate_name.name.split(' ')
        pattern = '\s*'.join(parts)  # Convert spaces to regex 0 or more whitespace characters.

        if not RelatedSensitivePhrase.objects.filter(
            content_type__pk=content_type.id,
            object_id=obj.id,
            phrase=pattern
        ).exists():
            RelatedSensitivePhrase.objects.create(
                obj=obj,
                phrase=pattern,
                replace_phrase=replace_phrase
            )
            num_phrases += 1

    return num_phrases


def check_interview_for_conflicts(interview, phrase, pattern, attrs):
    # First check the interviewer
    if phrase == pattern % tuple([getattr(interview.primary_interviewer, x, None) for x in attrs]):
        return True

    for person in interview.other_interviewers.all():
        if phrase == pattern % tuple([getattr(person, x, None) for x in attrs]):
            return True

    return False
