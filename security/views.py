import functools
import operator

from braces.views._access import AccessMixin

from cedar.utils.misc_utils import rgetattr
from cedar_settings.models import GeneralSetting
from security.models import SecurityLevel


class UserHasSecurityLevelQuerySetFilterMixin(object):
    """ This mixin overrides the get_queryset method to filter a queryset by the user's security level.
    Requires that the model being filtered defines a GenericRelation to SecurityLevel.  See library.Item for an example.
    """
    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.is_superuser:
            return qs

        level_range = [x[0] for x in SecurityLevel.level_choices]
        user_level = max(level_range)  # Default users to the lowest security level.
        user_security_level = SecurityLevel.objects.get_for_object(self.request.user)
        if user_security_level is not None:
            user_level = user_security_level.level

        obj_ids = []
        default_obj_level = GeneralSetting.objects.get("security_level_default")  # Default objects to the default level.
        for obj in qs:
            object_level = default_obj_level
            object_security_level = SecurityLevel.objects.get_for_object(obj)
            if object_security_level is not None:
                object_level = object_security_level.level

            if user_level <= object_level:
                obj_ids.append(obj.id)

        return qs.filter(id__in=obj_ids)


class UserHasObjectSecurityClearanceMixin(AccessMixin):
    """ This mixin only works with Update, Delete, and Detail Views because we need access to a single object!

    CBV Mixin allows you to define test that every user should pass
    to get access into view.
    Class Settings
        `test_func` - This is required to be a method that takes user
            instance and return True or False after checking conditions.
        `login_url` - the login url of site
        `redirect_field_name` - defaults to "next"
        `raise_exception` - defaults to False - raise 403 if set to True
    """
    object_attr = None
    relative_fallback_result = False  # When searching for a relative object this is the fallback result when no object is found.

    def test_clearance_func(self, user):
        # Super users can do what they want.
        if user.is_superuser:
            return True

        root_obj = self.get_object()
        if self.object_attr is not None:
            obj = rgetattr(root_obj, self.object_attr, None)

            if callable(obj):
                # The final attr could be a method if this is coming from a queryset.  all() first() etc
                obj = obj()

            if obj is None:
                # If relative objects don't exist, return the fallback
                return self.relative_fallback_result
        else:
            obj = root_obj

        # Attempt to iterate in case we have a queryset of objects to check.
        try:
            results = []
            for iter_obj in obj:
                results.append(self.test_object_clearance(user, iter_obj))

            if results:
                return functools.reduce(operator.or_, results)
            else:
                return self.relative_fallback_result

        except TypeError:
            return self.test_object_clearance(user, obj)

    def test_object_clearance(self, user, obj):
        level_range = [x[0] for x in SecurityLevel.level_choices]
        user_level = max(level_range)  # Default users to the lowest security level.
        user_security_level = SecurityLevel.objects.get_for_object(user)
        if user_security_level is not None:
            user_level = user_security_level.level

        object_level = GeneralSetting.objects.get("security_level_default")  # Default objects to the default level.
        object_security_level = SecurityLevel.objects.get_for_object(obj)
        if object_security_level is not None:
            object_level = object_security_level.level

        # Allow access to the object only if the user has an access level equal or lower to the object level.
        return user_level <= object_level


    def get_test_clearance_func(self):
        return getattr(self, "test_clearance_func")

    @staticmethod
    def add_user_to_form_kwargs(self, request, kwargs):
        kwargs['user'] = request.user

    def get_form_kwargs(self):
        # TODO This is untested.  If something goes wrong when adding security to a new model this is a good candidate.
        view_super = super()
        get_form_kwargs = getattr(view_super, "get_form_kwargs", None)
        if callable(get_form_kwargs):
            kwargs = get_form_kwargs()
            return self.add_user_to_form_kwargs(self.request, kwargs)

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_clearance_func()(request.user)

        if not user_test_result:
            return self.handle_no_permission(request)

        return super().dispatch(request, *args, **kwargs)
