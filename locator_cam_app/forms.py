from django import forms
from django.contrib.auth.models import User
from locator_cam_app.models import UserProfile, MomentPhoto, MomentThumbnail, Moment

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ('picture',)

class MomentPhotoForm(forms.ModelForm):
	class Meta:
		model = MomentPhoto
		fields = ('photo_base64',)

class MomentForm(forms.ModelForm):
	class Meta:
		model = Moment
		fields = ('description', 'latitude', 'longitude', 'pub_time_interval', 'channel')

class MomentThumbnailForm(forms.ModelForm):
	class Meta:
		model = MomentThumbnail
		fields = ('thumbnail_base64',)