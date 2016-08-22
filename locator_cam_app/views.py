import re
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from locator_cam_app.forms import UserForm, UserProfileForm, MomentPhotoForm, MomentThumbnailForm, MomentForm
from locator_cam_app.models import UserProfile, Moment, Channel


# Create your views here.

def index(request):
	if request.user.is_authenticated():
		# retrieve moments from me and my friends' profile
		my_profile = request.user.userprofile
		friends_profiles = UserProfile.objects.get(user__username=request.user.username).friends.all()		
		all_moments = Moment.objects.filter(Q(user__userprofile__in=friends_profiles) | Q(user__userprofile=my_profile))
		# all_moments_urls = [moment.thumbnail.url + ' ' + str(moment.pub_time) for moment in all_moments]
		return render(request, 'locator_cam_app/index.html', {'moments': all_moments})
	else:
		print('user is none')
	return render(request, 'locator_cam_app/index.html')

def register(request):
	registered = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()

			user.set_password(user.password)
			user.save()

			profile = profile_form.save(commit=False)
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			profile.save()

			registered = True
			message = 'Register successfully'
		else:
			"""
			>>> f.errors.as_data()
			{'sender': [ValidationError(['Enter a valid email address.'])],
			'subject': [ValidationError(['This field is required.'])]}
			"""
			message = ''
			for (field, errors) in user_form.errors.as_data().items():
				message += str(field) + ': '
				for error in errors:
					for error_message in error.messages:
						message += error_message + ' '
				message += '\n'

		return HttpResponse(json.dumps({'message': message}))

	else:
		user_form = UserForm()
		profile_form = UserProfileForm()
		return render(request, 'locator_cam_app/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)

		# the user information is returned as a json object in the http response
		user_info = {
			'username': None,
			'email': None,
			'friends': None,
			'error': None
		}

		if user:
			if user.is_active:
				login(request, user)

				# update the user information
				user_info['username'] = request.user.username
				user_info['email'] = request.user.email
				user_info['friends'] = [friend.user.username for friend in user.userprofile.friends.all()]
			else:
				user_info['error'] = 'Account disabled'
		else:
			user_info['error'] = 'Invalid credentials'

		return HttpResponse(json.dumps(user_info))
	else:
		return render(request, 'locator_cam_app/login.html', {})

@login_required
def search_user(request):
	users = []
	if request.method == 'POST':
		content_type = request.POST.get('content_type')
		username = request.POST.get('username')
		users = User.objects.filter(username__icontains=username)
		if content_type == 'JSON':
			res_json = {
				'users': [user.username for user in users]
			}
			return HttpResponse(json.dumps(res_json))

	return render(request, 'locator_cam_app/search_user.html', {'users': users})	

@login_required
def add_friend(request):
	if request.method == 'POST':
		content_type = request.POST.get('content_type')
		other_user_name = request.POST.get('username')
		other_user = User.objects.get(username=other_user_name)
		this_user = request.user
		if this_user == other_user:
			# adding the user itself as its friend is not allowed
			return HttpResponse(json.dumps({'message': 'error'})) if content_type == 'JSON' else HttpResponse('error')
		this_user.userprofile.friends.add(other_user.userprofile)
		message = "{0:s} became your friend!".format(other_user_name)
		return HttpResponse(json.dumps({'message': message})) if content_type == 'JSON' else HttpResponse(message)
	return redirect('/locator-cam/')

@login_required
def number_of_friends(request):
	if request.method == 'POST':
		content_type = request.POST.get('content_type')
		number_of_friends = User.objects.get(username=request.user.username).userprofile.friends.count()
		return HttpResponse(json.dumps({'number_of_friends': number_of_friends})) if content_type == 'JSON' else HttpResponse(number_of_friends)
	return HttpResponse('This API only supports POST request')

@login_required
def get_all_friends(request):
	if request.method == 'POST':
		content_type = request.POST.get('content_type')
		friends = [friend.user.username for friend in request.user.userprofile.friends.all()]
		return HttpResponse(json.dumps({'friends': friends})) if content_type == 'JSON' else HttpResponse(friends)
	return HttpResponse('This API only supports POST request')

@login_required
def logout_user(request):
	logout(request)
	return redirect('/locator-cam')

@login_required
def unfriend(request):
	if request.method == 'POST':
		content_type = request.POST.get('content_type')
		user = request.user
		username_to_unfriend = request.POST.get('username')
		user_to_unfriend = UserProfile.objects.get(user__username=username_to_unfriend)
		user.userprofile.friends.remove(user_to_unfriend)
		message = 'You unfriended {0:s}'.format(username_to_unfriend)
		messages.add_message(request, messages.INFO, message)
		return HttpResponse(json.dumps({'message': message})) if content_type == 'JSON' else redirect('/locator-cam')
	else:
		return HttpResponse('This API only supports POST request')

@login_required
def upload_moment(request):
	if request.method == 'POST':
		photo_form = MomentPhotoForm(request.POST, request.FILES)
		thumbnail_form = MomentThumbnailForm(request.POST, request.FILES)
		moment_form = MomentForm(request.POST, request.FILES)

		if photo_form.is_valid() and thumbnail_form.is_valid() and moment_form.is_valid():
			# upload the moment
			moment = moment_form.save(commit=False)
			moment.user = request.user
			channel_id = request.POST.get('channel_id')
			if channel_id is not None:
				channel_id_int = int(channel_id)
				moment.channel = Channel.objects.get(pk=channel_id_int)
			moment.save()
			# upload photo and thumbnail
			photo = photo_form.save(commit=False)
			photo.moment = moment
			photo.save()
			thumbnail = thumbnail_form.save(commit=False)
			thumbnail.moment = moment
			thumbnail.save()
			message = 'Your moment has been uploaded successfully'
		else:
			message = '{0:}\n{1:}'.format(photo_form.errors, moment_form.errors)

		if request.POST.get('content_type') == 'JSON':
			return HttpResponse(json.dumps({ 'message': message }))
		else:
			return HttpResponse(message)

	else:
		photo_form = MomentPhotoForm()
		thumbnail_form = MomentThumbnailForm()
		moment_form = MomentForm()

	return render(request, 'locator_cam_app/upload_moment.html', {'photo_form': photo_form, 'thumbnail_form': thumbnail_form, 'moment_form': moment_form})

@login_required
def fetch_moments(request):
	DEFAULT_QUERY_LIMIT = 10
	if request.method == 'POST':
		CONTENT_TYPE = request.META.get('CONTENT_TYPE')
		HTTP_ACCEPT = request.META.get('HTTP_ACCEPT')

		if re.search('application/json', CONTENT_TYPE, re.IGNORECASE) and \
			re.search('charset=utf-8', CONTENT_TYPE, re.IGNORECASE):
			# the request is in JSON format and encoded in utf-8
			json_data = json.loads(request.body.decode('utf-8'))
			# fetch moments published later than the latest moment in the front end
			published_later_than = json_data.get('published_later_than')
			# fetch moments published earlier than the earliest moment in the front end
			published_earlier_than = json_data.get('published_earlier_than')
			# the limit of how many moments we want to fetch
			query_limit = json_data.get('query_limit') or DEFAULT_QUERY_LIMIT
			# moments that already exist in the front end
			existing_moments_id = json_data.get('existing_moments_id')
			# which channel 
			channel_id = json_data.get('channel_id')
		else:
			published_later_than = request.POST.get('published_later_than') 
			published_earlier_than = request.POST.get('published_earlier_than') 
			query_limit = request.POST.get('query_limit') or DEFAULT_QUERY_LIMIT
			existing_moments_id = json.loads(request.POST.get('existing_moments_id'))

		latest_moment_pub_time_interval = None
		earlist_moment_pub_time_interval = None

		if len(existing_moments_id) > 0:
			if published_later_than or published_later_than == 'True':
				latest_moment_pub_time_interval = Moment.objects.get(pk=existing_moments_id[0]).pub_time_interval
			if published_earlier_than or published_earlier_than == 'True':
				earlist_moment_pub_time_interval = Moment.objects.get(pk=existing_moments_id[-1]).pub_time_interval

		my_profile = request.user.userprofile
		friends_profiles = UserProfile.objects.get(user__username=request.user.username).friends.all()

		if channel_id is not None:
			# if there is a channel, get a moment query set for the channel
			channel_id_int = int(channel_id)
			all_moments = Moment.objects.filter(channel__id=channel_id)
		else:
			# otherwise fetch moments not under any particular channel, i.e. public moments
			all_moments = Moment.objects.filter(channel__id__isnull=True)

		if latest_moment_pub_time_interval is not None:
			all_moments = all_moments.exclude(pk__in=existing_moments_id).\
			filter(Q(pub_time_interval__gte=latest_moment_pub_time_interval), \
			Q(user__userprofile__in=friends_profiles) | Q(user__userprofile=my_profile))[:query_limit]
		elif earlist_moment_pub_time_interval is not None:
			all_moments = all_moments.exclude(pk__in=existing_moments_id).\
			filter(Q(pub_time_interval__lte=earlist_moment_pub_time_interval), \
			Q(user__userprofile__in=friends_profiles) | Q(user__userprofile=my_profile))[:query_limit]
		else:
			all_moments = all_moments.exclude(pk__in=existing_moments_id).\
			filter(Q(user__userprofile__in=friends_profiles) | Q(user__userprofile=my_profile))[:query_limit]

		if HTTP_ACCEPT == 'application/json':
			moments_json = [{
				'id': moment.id,
				'username': moment.user.username,
				"description": moment.description,
				"latitude": moment.latitude,
				"longitude": moment.longitude,
				"pub_time_interval": moment.pub_time_interval,
				"thumbnail_base64": moment.momentthumbnail.thumbnail_base64
			} for moment in all_moments]
			return HttpResponse(json.dumps(moments_json))
		else:
			return render(request, 'locator_cam_app/index.html', {'moments': all_moments})
	else:
		return HttpResponse('This API only supports POST request')

@login_required
def delete_moment(request):
	if request.method == 'POST':
		Moment.objects.get(pk=request.POST.get('pk')).delete()
		return HttpResponse('moment deleted')
	else:
		return HttpResponseForbidden('Only support POST request.')

@login_required
def fetch_photo(request):
	if request.method == 'POST':
		content_type = request.POST.get('content_type')
		moment_id = request.POST.get('moment_id')
		photo_base64 = Moment.objects.get(pk=moment_id).momentphoto.photo_base64
		return HttpResponse(json.dumps({'photo_base64': photo_base64})) if content_type == 'JSON' else HttpResponse(photo_base64)
	else:
		return HttpResponse('This API only supports POST request')	

@login_required
def fetch_channels(request):
	profile = UserProfile.objects.get(user=request.user)
	channels = profile.membership_channels.all()
	channels_json = [{
						'channel_id': channel.id,
						'channel_name': channel.name,
						'description': channel.description,
						'num_members': channel.members.count(),
						'num_admins': channel.administrators.count()
						} 
					for channel in channels]
	return HttpResponse(json.dumps(channels_json))


@login_required
def fetch_channels_count(request):
	profile = UserProfile.objects.get(user=request.user)
	channels_count = profile.membership_channels.count()
	channels_count_json = {'channels_count': channels_count}
	return HttpResponse(json.dumps(channels_count_json))


@login_required
def create_channel(request):
	if request.method == 'POST' and re.search('application/json', request.META.get('CONTENT_TYPE'), re.IGNORECASE):
		json_data = json.loads(request.body.decode('utf-8'))
		channel_name = json_data.get('channel_name')
		channel_description = json_data.get('channel_description') if json_data.get('channel_description') is not None else ''
		if Channel.objects.filter(name=channel_name).count() > 0:
			message = 'The channel name exists, please choose another one'
		else:
			channel = Channel(name=channel_name, user_created=request.user.userprofile, description=channel_description)
			channel.save()
			channel.members.add(request.user.userprofile)
			channel.administrators.add(request.user.userprofile)
			channel.save()
			message = 'Channel {0:s} was created successfully'.format(channel_name)
		return HttpResponse(json.dumps({'message': message}))
	else:
		return HttpResponseNotFound()


@login_required
def add_member_to_channel(request):
	if request.method == 'POST' and re.search('application/json', request.META.get('CONTENT_TYPE'), re.IGNORECASE):
		json_data = json.loads(request.body.decode('utf-8'))
		channel_id = int(json_data.get('channel_id'))
		username_to_be_added = json_data.get('username_to_be_added')
		channel = get_object_or_404(Channel, pk=channel_id)
		user_to_be_added = get_object_or_404(UserProfile, user__username=username_to_be_added)

		if request.user.userprofile in channel.administrators.all():
			channel.members.add(user_to_be_added)
			message = 'User {0:s} became a member of channel {1:s}'.format(username_to_be_added, channel.name)
		else:
			message = 'Error: you are not the administrator of this channel'
		return HttpResponse(json.dumps({'message': message}))
	else:
		return HttpResponseNotFound()


@login_required
def add_administrator_to_channel(request):
	if request.method == 'POST' and re.search('application/json', request.META.get('CONTENT_TYPE'), re.IGNORECASE):
		json_data = json.loads(request.body.decode('utf-8'))
		channel_id = int(json_data.get('channel_id'))
		username_to_be_added = json_data.get('username_to_be_added')
		channel = get_object_or_404(Channel, pk=channel_id)
		user_to_be_added = get_object_or_404(UserProfile, user__username=username_to_be_added)

		if request.user.userprofile in channel.administrators.all():
			channel.administrators.add(user_to_be_added)
			# an administrator becomes a member automatically
			channel.members.add(user_to_be_added)
			message = 'User {0:s} became an administrator of channel {1:s}'.format(username_to_be_added, channel.name)
		else:
			message = 'Only administrators of this channel are allowed to add an administrator'
		return HttpResponse(json.dumps({'message': message}))
	else:
		return HttpResponseNotFound()


@login_required
def get_channel_members(request):
	if request.method == 'POST' and re.search('application/json', request.META.get('CONTENT_TYPE'), re.IGNORECASE):
		json_data = json.loads(request.body.decode('utf-8'))
		channel_id = int(json_data.get('channel_id'))		
		channel = get_object_or_404(Channel, pk=channel_id)
		members = channel.members.all()
		if request.user.userprofile in members:
			members = [member.user.username for member in members]
			return HttpResponse(json.dumps({'members': members}))
		else:
			message = 'Error: you are not a member of this channel.'
			return HttpResponse(json.dumps({'message': message}))
	else:
		return HttpResponseNotFound()


@login_required
def get_channel_administrators(request):
	if request.method == 'POST' and re.search('application/json', request.META.get('CONTENT_TYPE'), re.IGNORECASE):
		json_data = json.loads(request.body.decode('utf-8'))
		channel_id = json_data.get('channel_id')
		channel = get_object_or_404(Channel, pk=channel_id)

		if request.user.userprofile in channel.members.all():
			administrators = [administrator.user.username for administrator in channel.administrators.all()]
			return HttpResponse(json.dumps({'administrators': administrators}))
		else:
			message = 'Error: you are not a member of this channel.'
			return HttpResponse(json.dumps({'message': message}))
	else:
		return HttpResponseNotFound()


@login_required
def remove_member_from_channel(request):
	if request.method == 'POST' and re.search('application/json', request.META.get('CONTENT_TYPE'), re.IGNORECASE):
		json_data = json.loads(request.body.decode('utf-8'))
		channel_id = json_data.get('channel_id')
		member_username = json_data.get('member_username')
		channel = get_object_or_404(Channel, pk=channel_id)
		member_to_be_removed = get_object_or_404(UserProfile, user__username=member_username)

		if request.user.userprofile in channel.administrators.all():
			channel.members.remove(member_to_be_removed)
			message = '{0:s} has been removed from the members of channel {1:s}'.format(member_username, channel.name)
		else:
			message = 'Only administrators of this channel are allowed to remove members.'

		return HttpResponse(json.dumps({'message': message}))

	else:
		return HttpResponseNotFound()


@login_required
def remove_administrator_from_channel(request):
	if request.method == 'POST' and re.search('application/json', request.META.get('CONTENT_TYPE'), re.IGNORECASE):
		json_data = json.loads(request.body.decode('utf-8'))
		channel_id = json_data.get('channel_id')
		administrator_username = json_data.get('administrator_username')
		channel = get_object_or_404(Channel, pk=channel_id)
		administrator_to_be_removed = get_object_or_404(UserProfile, user__username=administrator_username)

		if request.user.userprofile in channel.administrators.all():
			channel.administrators.remove(administrator_to_be_removed)
			message = '{0:s} has been removed from the administrators of channel {1:s}'.format(administrator_username, channel.name)
		else:
			message = 'Only administrators of this channel are allowed to remove administrators.'

		return HttpResponse(json.dumps({'message': message}))

	else:
		return HttpResponseNotFound()


@login_required
def delete_channel(request):
	if request.method == 'POST' and re.search('application/json', request.META.get('CONTENT_TYPE'), re.IGNORECASE):
		json_data = json.loads(request.body.decode('utf-8'))
		channel_id = json_data.get('channel_id')
		channel = get_object_or_404(Channel, pk=channel_id)
		
		if request.user.userprofile in channel.administrators.all():
			channel.delete()
			message = 'Channel {0:s} has been deleted successfully.'.format(channel.name)
		else:
			message = 'Only administrators of this channel are allowed to delete this channel.'
		return HttpResponse(json.dumps({'message': message}))
	else:
		return HttpResponseNotFound


@login_required
def leave_channel(request):
	if request.method == 'POST' and re.search('application/json', request.META.get('CONTENT_TYPE'), re.IGNORECASE):
		json_data = json.loads(request.body.decode('utf-8'))
		channel_id = json_data.get('channel_id')
		channel = get_object_or_404(Channel, pk=channel_id)

		if channel.administrators.filter(user__username=request.user.username).exists() and \
			channel.administrators.count() == 1:
			# this user is the only administrator of this channel, the user must not leave
			message = 'You are the only administrator of this channel, you cannot leave. You can delete the channel instead.'
		elif channel.members.filter(user__username=request.user.username).exists():
			# removed from members
			channel.members.remove(request.user.userprofile)
			message = 'You left channel "%s".' % (channel.name)
		else:
			# not a member
			message = 'You are not a member of channel "%s".' % (channel.name)

		return HttpResponse(json.dumps({'message': message}))
	else:
		return HttpResponseNotFound



@login_required
def fetch_incoming_friend_requests(request):
	""" fetch friend requests from others """
	pass


@login_required
def accept_friend_request(request):
	pass

@login_required
def fetch_incoming_channel_invitations(request):
	""" fetch channel invites from others """
	pass





