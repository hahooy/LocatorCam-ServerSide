from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from locator_cam_app.forms import UserForm, UserProfileForm, PhotoForm, MomentForm
from locator_cam_app.models import UserProfile, Moment


# Create your views here.

def index(request):
	if request.user.is_authenticated():
		my_moments = UserProfile.objects.get(user__username=request.user.username).user.moment_set.all()
		my_moments_urls = [moment.thumbnail.url for moment in my_moments]
		friend_profiles = UserProfile.objects.get(user__username=request.user.username).friends.all()
		friend_moments = Moment.objects.filter(user__userprofile__in=friend_profiles)
		friend_moments_urls = [moment.thumbnail.url for moment in friend_moments]
		print('url of my moments: {0:}'.format(my_moments_urls))
		return render(request, 'locator_cam_app/index.html', {'moments': my_moments_urls + friend_moments_urls})
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

			#user = authenticate(username=user.username, password=request.POST.get('password'))
			#login(request, user)
			registered = True
		else:
			print('{0:}\n{1:}'.format(user_form.errors, profile_form.errors))

	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render(request, 'locator_cam_app/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				return redirect('/locator-cam')
			else:
				return HttpResponse("Your account is disabled.")
		else:
			return HttpResponse("invalid credentials")
	else:
		return render(request, 'locator_cam_app/login.html', {})

@login_required
def search_user(request):
	users = []
	if request.method == 'POST':
		username = request.POST.get('username')
		users = User.objects.filter(username__icontains=username)
	return render(request, 'locator_cam_app/search_user.html', {'users': users})	

@login_required
def add_friend(request):
	if request.method == 'POST':
		other_user_name = request.POST.get('username')
		other_user = User.objects.get(username=other_user_name)
		this_user = request.user
		this_user.userprofile.friends.add(other_user.userprofile)
		return HttpResponse("{0:s} became your friend!".format(other_user_name))
	return redirect('/locator-cam/')

@login_required
def logout_user(request):
	logout(request)
	return redirect('/locator-cam')

@login_required
def unfriend(request):
	if request.method == 'POST':
		user = request.user
		username_to_unfriend = request.POST.get('username')
		user_to_unfriend = UserProfile.objects.get(user__username=username_to_unfriend)
		user.userprofile.friends.remove(user_to_unfriend)
		messages.add_message(request, messages.INFO, 'You unfriended {0:s}'.format(username_to_unfriend))
		return redirect('/locator-cam')
	else:
		return redirect('404')

@login_required
def upload_moment(request):
	if request.method == 'POST':
		photo_form = PhotoForm(request.POST, request.FILES)
		moment_form = MomentForm(request.POST, request.FILES)

		if photo_form.is_valid() and moment_form.is_valid():
			photo = photo_form.save()
			moment = moment_form.save(commit=False)

			moment.photo = photo
			moment.user = request.user
			moment.save()

			return HttpResponse('Your moment has been uploaded successfully')
		else:
			print('{0:}\n{1:}'.format(photo_form.errors, moment_form.errors))

	else:
		photo_form = PhotoForm()
		moment_form = MomentForm()

	return render(request, 'locator_cam_app/upload_moment.html', {'photo_form': photo_form, 'moment_form': moment_form})

















