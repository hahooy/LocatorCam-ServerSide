from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^register/$', views.register, name='register'),
	url(r'^login/$', views.user_login, name='login'),
	url(r'^search-user/$', views.search_user, name='search-user'),
	url(r'^add-friend/$', views.add_friend, name='add-friend'),
	url(r'^logout/$', views.logout_user, name='logout'),
	url(r'^unfriend/$', views.unfriend, name='unfriend')
]