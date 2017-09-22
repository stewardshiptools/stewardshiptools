from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'communication', views.CommunicationViewSet, 'communication')

urlpatterns = [
    url(r'^$', views.CommunicationDashboardView.as_view(), name='dashboard'),

    url(r'^list/$', views.CommunicationListView.as_view(), name='communication-list'),

    url(r'^detail/(?P<pk>[0-9]+)/$', views.CommunicationDetailView.as_view(), name='communication-detail'),
    url(r'^new/$', views.CommunicationCreateView.as_view(), name='communication-create'),
    url(r'^edit/(?P<pk>[0-9]+)/$', views.CommunicationUpdateView.as_view(), name='communication-update'),
    url(r'^delete/(?P<pk>[0-9]+)/$', views.CommunicationDeleteView.as_view(), name='communication-delete'),

    # url(r'^phone/new/$', views.PhoneCallCreateView.as_view(), name='phonecall-create'),
    url(r'^(?P<related_ct_id>\d+)/(?P<related_oid>\d+)/phone/new/$', views.PhoneCallCreateView.as_view(), name='phonecall-create'),
    url(r'^(?P<related_ct_id>\d+)/(?P<related_oid>\d+)/fax/new/$', views.FaxCreateView.as_view(), name='fax-create'),
    url(r'^(?P<related_ct_id>\d+)/(?P<related_oid>\d+)/letter/new/$', views.LetterCreateView.as_view(), name='letter-create'),

    url(r'^message/(?P<pk>[0-9]+)/$', views.MessageDetailView.as_view(), name='message-detail'),
    url(r'^fax/(?P<pk>[0-9]+)/$', views.FaxDetailView.as_view(), name='fax-detail'),
    url(r'^letter/(?P<pk>[0-9]+)/$', views.LetterDetailView.as_view(), name='letter-detail'),
    url(r'^phone/(?P<pk>[0-9]+)/$', views.PhoneCallDetailView.as_view(), name='phonecall-detail'),

    url(r'^prefix/new$', views.HarvestCodePrefixCreateView.as_view(), name='prefix-create'),
    url(r'^prefix/list$', views.HarvestCodePrefixListView.as_view(), name='prefix-list'),

    url(r'^mailharvest/manage$', views.MailHarvestManageView.as_view(), name='mailharvest-manage'),
    url(r'^mailharvest/mailaccount/run/(?P<pk>[0-9]+)/$', views.MailHarvestRunMailAccountView.as_view(), name='mailharvest-run-account'),
    url(r'^mailharvest/mailaccount/status/(?P<mail_account_id>[0-9]+)/$', views.check_task_mail_account_status, name='mailharvest-run-status'),
    url(r'^mailharvest/mailaccount/status/all/$', views.check_task_mail_account_status_all, name='mailharvest-run-status-all'),

    url(r'^initiate_gmail_auth/$', views.initiate_gmail_auth, name='initiate_gmail_auth'),
    url(r'^authorize_gmail/$', views.authorize_gmail, name='authorize_gmail'),
    url(r'^authorize_gmail_success/(?P<credentials_id>\d+)/$', views.authorize_gmail_success, name='authorize_gmail_success'),

    url(r'^log/download/$', views.serve_communication_log_file, name='log-download'),

    # Rest API URL routing.
    url(r'^api/', include(router.urls, namespace='api')),
]
