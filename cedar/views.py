from __future__ import absolute_import
import csv
from anyjson import serialize as json_serialize

from django.views.generic import TemplateView, UpdateView, FormView

from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator

from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import Http404, HttpResponse

from cedar.celery import app as celery_app
from celery.five import items

from .forms import UserSettingsForm, UserSettingsFormset

from help.mixins import HelpContextMixin

import celery.task  # noqa


class HomeView(TemplateView):
    template_name = 'home.html'


class UpdateUserSettingsView(HelpContextMixin, UpdateView):
    template_name = 'cedar/user-settings-form.html'
    form_class = UserSettingsForm
    model = User
    page_help_name = 'cedar:user-settings-update'

    def get_context_data(self, **kwargs):
        context = super(UpdateUserSettingsView, self).get_context_data(**kwargs)
        if self.request.POST:
            crm_person_formset = UserSettingsFormset(self.request.POST, self.request.FILES, instance=self.request.user)
            context['crm_person_formset'] = crm_person_formset

        else:
            context['crm_person_formset'] = UserSettingsFormset(instance=self.request.user)

        return context

    def form_valid(self, form):
        # Check the inline user settings formset:
        user_settings_formset = UserSettingsFormset(self.request.POST, self.request.FILES, instance=form.instance)
        if user_settings_formset.is_valid():
            user_settings_formset.save()
            return super(UpdateUserSettingsView, self).form_valid(form)
        else:
            return super(UpdateUserSettingsView, self).form_invalid(form)

    # Overriding get object here lets us call up the view without
    # providing a PK because we use the request.user object instead.
    def get_object(self, queryset=None):
        return self.request.user

        # def get_form(self, form_class=None):
        #     return self.form_class(user=self.request.user)
        #

    def get_success_url(self):
        return reverse('user-settings')


class UserPasswordUpdateView(FormView):
    form_class = PasswordChangeForm
    # success_url = reverse('profile_view_details')
    template_name = 'registration/password_change_form.html'

    def get_form_kwargs(self):
        kwargs = super(UserPasswordUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        # messages.add_message(self.request, messages.INFO, _('profile changed'))
        return super(UserPasswordUpdateView, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserPasswordUpdateView, self).dispatch(*args, **kwargs)


class Cedar404View(TemplateView):
    template_name = '404.html'


class Cedar403View(TemplateView):
    template_name = '403.html'


def JsonResponse(response):
    return HttpResponse(json_serialize(response), content_type='application/json')


# Need to overwrite the view from djcelery because pip installs with python2 things for some reason...
def celery_task_view(task):
    """
    Decorator turning any task into a view that applies the task
    asynchronously. Keyword arguments (via URLconf, etc.) will
    supercede GET or POST parameters when there are conflicts.
    Returns a JSON dictionary containing the keys ``ok``, and
        ``task_id``.
    """

    def _applier(request, **options):
        kwargs = request.POST if request.method == 'POST' else request.GET
        # no multivalue
        kwargs = {k: v for k, v in items(kwargs)}
        if options:
            kwargs.update(options)
        result = task.apply_async(kwargs=kwargs)
        return JsonResponse({'ok': 'true', 'task_id': result.task_id})

    return _applier


@login_required()
def apply_celery_task(request, task_name):
    """
    View applying a task.
    **Note:** Please use this with caution. Preferably you shouldn't make this
        publicly accessible without ensuring your code is safe!
    """
    tasks = celery_app.tasks
    print(tasks.keys())
    try:
        task = tasks[task_name]
    except KeyError:
        raise Http404('apply: no such task')

    # Later on we can add code here to make sure the tasks applied are in a white-list.

    return celery_task_view(task)(request)


def revoke_celery_task(request, task_id):
    task = celery_app.AsyncResult(task_id)
    task.revoke(terminate=True)
    return JsonResponse({'terminated': 'true', 'task_id': task_id})
