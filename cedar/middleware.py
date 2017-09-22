from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
# from django.http import HttpResponseForbidden

# todo: refactor the restricted group stuff. eg make 'allow' list into a list of regex patterns? hm or tag paths in urls.py?

'''
This is a ripoff of development.middleware.RestrictAccessMiddleware.
This will only check if a user is authenticated and if not, redirects straight
to the XML Generator page.
'''
restricted_groups = {
    'anonymous_xml_redirect': {
        'allow': [
            reverse('development:ser-create'),
        ],
        'redirect': reverse('development:ser-create'),
    }
}


class AnonymousXMLGeneratorAccessMiddleware(object):
    """
    Restricts access for anonymous users to only the pages that deal with generating XML.
    """
    def process_request(self, request):
        if request.user.is_anonymous():
            redirect_path = None
            path_ok = False

            if request.path in restricted_groups['anonymous_xml_redirect']['allow']:
                path_ok = True
            else:
                redirect_path = restricted_groups['anonymous_xml_redirect']['redirect']

            if not path_ok:
                return HttpResponseRedirect(redirect_path)

        return None