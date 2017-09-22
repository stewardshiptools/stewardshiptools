# cedar_settings/utils/parsers.py


def parse_choices(text, with_blank=True, blank_string="----------"):
    """ Parses structured text into a list of tuples for use by CharField choices.

    :param text: A list of CharField choices structured one choice per line as key|value
    :return: A list of tuples
    """
    if text is None:
        return None

    choices = []

    if with_blank:
        choices.append((None, blank_string))

    choice_strings = text.split("\n")
    for choice_string in choice_strings:
        if choice_string:  # Ignore empty lines
            parts = choice_string.split("|")
            choices.append((parts[0].strip(), parts[1].strip()))

    return choices


def get_choice_value(choices_text, choice):
    '''
    Takes choice settings text, the choice ID, and returns the value that ID corresponds to.
    :param choices_text: A list of CharField choices structured one choice per line as key|value
    :param choice: ID of the choice you want
    :return: Value of the choice. None if not found
    '''
    if not choice:
        return ""

    for id, val in parse_choices(choices_text):
        if id == choice:
            return val

    raise LookupError("Supplied choice parameter (\"{}\") not found in choice list".format(choice))
