from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^booking_in_form/$', views.booking_in_form, name='booking_in_form'),
    url(r'^autotask_login/$', views.autotask_login, name='autotask_login'),
    url(r'^create_picklist', views.create_picklist, name='create_picklist'),
    url(r'^$', views.index, name='index'),
    url(r'^create_ticket/(?P<id>[0-9]+)/$', views.create_ticket, name='create_ticket'),
    url(r'^create_upsell/(?P<id>[0-9]+)/$', views.create_upsell, name='create_upsell'),
    url(r'^create_home_user_ticket/(?P<id>[0-9]+)/', views.create_home_user_ticket, name='create_home_user_ticket'),
    url(r'^edit_ataccount/(?P<id>[0-9]+)/$', views.edit_ataccount, name='edit_ataccount'),
    url(r'^ataccount/(?P<id>[0-9]+)/$', views.ataccount, name='ataccount'),
    url(r'^ataccount/(?P<account_id>[0-9]+)/ticket/(?P<ticket_id>[0-9]+)/$', views.ticket_detail, name='ticket_detail'),
]
