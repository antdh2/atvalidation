from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^account/profile/(?P<id>[0-9]+)/input_validation/$', views.input_validation, name='input_validation'),
    url(r'^delete_validation_group/(?P<id>[0-9]+)', views.delete_validation_group, name='delete_validation_group'),
    url(r'^account/profile/(?P<id>[0-9]+)/$', views.profile, name='profile'),
    url(r'^create_picklist', views.create_picklist_database, name='create_picklist_database'),
    url(r'^$', views.index, name='index'),
    url(r'^create_ticket/(?P<id>[0-9]+)/$', views.create_ticket, name='create_ticket'),
    url(r'^create_home_user_ticket/(?P<id>[0-9]+)/', views.create_home_user_ticket, name='create_home_user_ticket'),
    url(r"^account/signup/$", views.SignupView.as_view(), name="account_signup"),
    url(r'^account/', include('account.urls')),
]
