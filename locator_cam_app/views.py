from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from locator_cam_app.forms import UserForm, UserProfileForm, PhotoForm, MomentForm
from locator_cam_app.models import UserProfile, Moment


import json


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

		info = {'error': None} # the response JSON object containing error information

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
		else:
			info['error'] = '{0:}{1:}'.format(user_form.errors, profile_form.errors)

		return HttpResponse(json.dumps(info))

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
		photo_form = PhotoForm(request.POST, request.FILES)
		moment_form = MomentForm(request.POST, request.FILES)

		if photo_form.is_valid() and moment_form.is_valid():
			moment = moment_form.save(commit=False)
			moment.user = request.user
			moment.save()
			photo = photo_form.save(commit=False)
			photo.moment = moment
			photo.save()
			message = 'Your moment has been uploaded successfully'
		else:
			message = '{0:}\n{1:}'.format(photo_form.errors, moment_form.errors)

		if request.POST.get('content_type') == 'JSON':
			return HttpResponse(json.dumps({ 'message': message }))
		else:
			return HttpResponse(message)

	else:
		photo_form = PhotoForm()
		moment_form = MomentForm()

	return render(request, 'locator_cam_app/upload_moment.html', {'photo_form': photo_form, 'moment_form': moment_form})

@login_required
def fetch_moments(request):
	DEFAULT_QUERY_LIMIT = 10
	if request.method == 'POST':
		starting_time = request.POST.get('starting_time') # fetch moments published later than this time
		ending_time = request.POST.get('ending_time') # fetch moments published earlier than this time
		query_limit = request.POST.get('query_limit') or DEFAULT_QUERY_LIMIT
		my_profile = request.user.userprofile
		friends_profiles = UserProfile.objects.get(user__username=request.user.username).friends.all()
		if ending_time is not None and starting_time is not None:
			ending_time_float = float(ending_time)
			starting_time_float = float(starting_time)
			all_moments = Moment.objects.filter(Q(pub_time_interval__lt=ending_time), Q(pub_time_interval__gt=starting_time), Q(user__userprofile__in=friends_profiles) | Q(user__userprofile=my_profile))[:query_limit]
		elif ending_time is not None:
			ending_time_float = float(ending_time)
			all_moments = Moment.objects.filter(Q(pub_time_interval__lt=ending_time), Q(user__userprofile__in=friends_profiles) | Q(user__userprofile=my_profile))[:query_limit]
		elif starting_time is not None:
			starting_time_float = float(starting_time)
			print(starting_time_float)
			all_moments = Moment.objects.filter(Q(pub_time_interval__gt=starting_time), Q(user__userprofile__in=friends_profiles) | Q(user__userprofile=my_profile))[:query_limit]
			if len(all_moments) > 0:
				print(all_moments[0].pub_time_interval)
		else:
			all_moments = Moment.objects.filter(Q(user__userprofile__in=friends_profiles) | Q(user__userprofile=my_profile))[:query_limit]
		if request.POST.get('content_type') == 'JSON':
			moments_json = [{
				'id': moment.id,
				'username': moment.user.username,
				"description": moment.description,
				"latitude": moment.latitude,
				"longitude": moment.longitude,
				"pub_time_interval": moment.pub_time_interval,
				"thumbnail_base64": moment.thumbnail_base64
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
		photo_base64 = Moment.objects.get(pk=moment_id).photo.photo_base64
		return HttpResponse(json.dumps({'photo_base64': photo_base64})) if content_type == 'JSON' else HttpResponse(photo_base64)
	else:
		return HttpResponse('This API only supports POST request')	











