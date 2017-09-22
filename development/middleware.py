from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
# from django.http import HttpResponseForbidden

# todo: refactor the restricted group stuff. eg make 'allow' list into a list of regex patterns? hm or tag paths in urls.py?

'''
Set the groups and redirects for restricted groups.
The process_request() method below checks if the user is in the specified group
and then compares the request url against the urls in the 'allow' list. If the
requested url is not in the allow group, it will redirect to the 'redirect' url.
Note for users that belong to multiple restricted_groups: process_request() isn't
smart enough to know which url redirect to use, so it will use the last one it
encounters for that user's groups.
Note you will get weird redirect loops if you're not careful with your allow/redirect
paths.
'''
restricted_groups = {
    'restricted_SER': {
        'allow': [
            reverse('development:ser-create'),
            reverse('login'),
            reverse('logout')
        ],
        'redirect': reverse('development:ser-create'),
    }
}


class RestrictAccessMiddleware(object):
    """
    Restricts access for users that belong to specified restricted groups. This shouldn't replace
    regular permission checking, instead should restrict a user to areas of the site
    where adding regular permissions would be ownerous.
    EG External users generating XML need ONLY to see the XML generate page.

    I think this could be expanded to control areas of access depending on
    what parts of C8 the client has paid to use.
    """
    def process_request(self, request):
        user_groups = request.user.groups.filter(name__in=restricted_groups.keys())
        if user_groups.exists():
            redirect_path = None
            path_ok = False
            for group in user_groups:
                if request.path in restricted_groups[group.name]['allow']:
                    path_ok = True
                    break
                else:
                    # save the redirect url:
                    redirect_path = restricted_groups[group.name]['redirect']

            if not path_ok:
                return HttpResponseRedirect(redirect_path)

        return None