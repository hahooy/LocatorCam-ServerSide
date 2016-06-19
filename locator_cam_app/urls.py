from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^register/$', views.register, name='register'),
	url(r'^login/$', views.user_login, name='login'),
	url(r'^search-user/$', views.search_user, name='search-user'),
	url(r'^add-friend/$', views.add_friend, name='add-friend'),
	url(r'^logout/$', views.logout_user, name='logout'),
	url(r'^unfriend/$', views.unfriend, name='unfriend'),
	url(r'^upload-moment/$', views.upload_moment, name='upload-moment'),
	url(r'^fetch-moments/$', views.fetch_moments, name='fetch-moments'),
	url(r'^delete-moment/$', views.delete_moment, name='delete-moment'),
	url(r'^fetch-photo/$', views.fetch_photo, name='fetch-photo'),
	url(r'^number-of-friends/$', views.number_of_friends, name='number-of-friends'),
	url(r'^get-all-friends/$', views.get_all_friends, name='get-all-friends'),
	url(r'^fetch-channels/$', views.fetch_channels, name='fetch-channels'),
	url(r'^create-channel/$', views.create_channel, name='create-channel'),
	url(r'^add-member-to-channel/$', views.add_member_to_channel, name='create-channel'),
	url(r'^get-channel-members/$', views.get_channel_members, name='get-channel-members')
]