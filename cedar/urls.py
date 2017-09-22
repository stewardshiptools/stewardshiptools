"""cedar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/

"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.contrib.auth.decorators import login_required

from djcelery.views import is_task_successful, task_status

from . import views
from cedar.forms import CedarPasswordResetForm

from heritage.forms import HeritageAssetForm

urlpatterns = [
    url(r'^$', login_required(views.HomeView.as_view()), name='home'),
    url(r'^spatialtools/', include('geoinfo.urls', namespace='geoinfo')),

    url(r'^heritage/', include('heritage.urls', namespace='heritage')),
    url(r'^heritage/', include('library.urls', namespace='heritage-library', app_name='library'),
        {
            'default_asset_model': 'heritage.heritageasset',
            'default_asset_modelform': HeritageAssetForm}
        ),

    url(r'^development/', include('development.urls', namespace='development')),
    # url(r'^development/', include('library.urls', namespace='development-library', app_name='library')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^assets/', include('assets.urls', namespace='assets')),
    url(r'^help/', include('help.urls', namespace='help')),
    url(r'^communication/', include('communication.urls', namespace='communication')),
    url(r'^eco/', include('ecosystems.urls', namespace='ecosystems')),

    # url(r'^secure/(?P<file_id>[0-9]+)', login_required(assets.views.download_private_file), name='secure'),
    # url(r'^{0}/(?P<file_id>[0-9]+)'.format(settings.SECURE_MEDIA_URL.lstrip('/')), login_required(assets.views.download_private_file), name='secure_handler'),

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    url(r'^crm/', include('crm.urls', namespace="crm")),
    url(r'^maps/', include('maps.urls', namespace="maps")),
    url(r'^communitymap/', include('communitymap.urls', namespace="communitymap")),

    # AUTH and USER SETTINGS:
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': settings.LOGIN_URL}, name='logout'),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(
        r'^password/reset/$',
        'django.contrib.auth.views.password_reset',
        name='password_reset',
        kwargs={
            'template_name': 'password_reset_form.html',
            'email_template_name': 'password_reset.txt',
            'html_email_template_name': 'password_reset_email.html',
            'subject_template_name': 'password_reset_subject.txt',
            'password_reset_form': CedarPasswordResetForm
        }
    ),
    url(
        r'^password/reset/done/$',
        'django.contrib.auth.views.password_reset_done',
        name='password_reset_done',
        kwargs={
            'template_name': 'password_reset_done.html'
        }
    ),
    url(
        r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        name='password_reset_confirm',
        kwargs={
            'template_name': 'password_reset_confirm.html',
            'post_reset_redirect': 'password_reset_complete'
        }
    ),
    url(
        r'^password/reset/complete/$',
        'django.contrib.auth.views.password_reset_complete',
        name='password_reset_complete',
        kwargs={
            'template_name': 'password_reset_complete.html',
        }
    ),
    url(r'^user-settings/$', login_required(views.UpdateUserSettingsView.as_view()), name='user-settings'),
    url(
        r'^user-settings/change-password$',
        'django.contrib.auth.views.password_change',
        name='change-password',
        kwargs={
            'template_name': 'user_password_change_form.html',
            'post_change_redirect': 'change-password-done',
        }
    ),
    url(
        r'^user-settings/change-password-done$',
        'django.contrib.auth.views.password_change_done',
        name='change-password-done',
        kwargs={'template_name': 'user_password_change_done.html'}
    ),

    # Search - this is the site-wide search. Heritage has it's own.
    # url(r'^search/', login_required(assets.views.SecureAssetSearchView.as_view()), name='search'),

    # Provide a way to access the 404 page outside of DEBUG mode.
    url(r'^404/', views.Cedar404View.as_view(), name='404'),
    # Provide a way to access the 403 page outside of DEBUG mode.
    url(r'^403/', views.Cedar403View.as_view(), name='403'),

    # Additionally, we include login URLs for the browsable API.
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Core celery views to expose webhooks.
    url(r'^celery/apply/(?P<task_name>.*)/$', views.apply_celery_task, name='celery-apply'),
    url(r'^celery/(?P<task_id>[\w\d\-]+)/done/?$', is_task_successful, name='celery-is_task_successful'),
    url(r'^celery/(?P<task_id>[\w\d\-]+)/status/?$', task_status, name='celery-task_status'),
    url(r'^celery/(?P<task_id>[\w\d\-]+)/revoke/?$', views.revoke_celery_task, name='celery-task_revoke'),

    # discussion top-level
    url(r'^comments/', include('django_comments.urls')),

    # Django taggit autosuggest top-level
    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    url(r'^tags/', include('tags.urls', namespace='tags'))
]

# Rename Admin header here:
admin.site.site_header = 'Cedar 8 Administration'
