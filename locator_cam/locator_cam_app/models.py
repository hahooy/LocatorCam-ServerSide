from django.db import models
from django.contrib.auth.models import User
import hashlib

class Photo(models.Model):
	base64_image_str = models.TextField()

	def __str__(self):
		return self.base64_image_str

class Moment(models.Model):
	description = models.TextField()
	latitude = models.FloatField()
	longitude = models.FloatField()
	user_profile = models.ForeignKey(User)
	photo = models.OneToOneField(Photo)
	thumbnail_base64 = models.TextField()
	pub_time = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.description

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	picture = models.ImageField(upload_to='profile_images', blank=True)
	friends = models.ManyToManyField('self')

	def __str__(self):
		return self.user.username