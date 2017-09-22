# recurse_subclasses - gets a list of all child classes of the super class,
# the return list includes the top-level parent.
# Arguments:
#   parentclass : top-level parent
#   classlist: always submit an empty list: []
def recurse_subclasses(parentclass, classlist):
    classlist.append(parentclass)
    if len(parentclass.__subclasses__()) > 0:
        for childclass in parentclass.__subclasses__():
            recurse_subclasses(childclass, classlist)
    return classlist


def get_back_url(request):
    return request.META.get('HTTP_REFERER', '')


def get_back_url_from_context(context):
    return get_back_url(context.request)

def rgetattr(obj, attr, *args):
    """ A recirsive implementation of getattr. Accepts dotted attributes attr1.attr2.attr3...

    :param obj:
    :param attr:
    :return:
    """
    if "." not in attr:
        if args:
            return getattr(obj, attr, args[0])
        else:
            return getattr(obj, attr)
    else:
        split_attrs = attr.split('.')

        if args:
            return rgetattr(getattr(obj, split_attrs[0]), '.'.join(split_attrs[1:]), args[0])
        else:
            return rgetattr(getattr(obj, split_attrs[0]), '.'.join(split_attrs[1:]))
