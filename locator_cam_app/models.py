from django.db import models
from django.contrib.auth.models import User
import hashlib



class Moment(models.Model):
	description = models.TextField()
	latitude = models.FloatField()
	longitude = models.FloatField()
	user = models.ForeignKey(User)
	#photo = models.OneToOneField(Photo)
	thumbnail = models.ImageField(upload_to='thumbnail_images', blank=True)
	#thumbnail_base64 = models.TextField()
	pub_time = models.DateTimeField(db_index=True, auto_now_add=True)

	class Meta:
		ordering = ['-pub_time']

	def __str__(self):
		return self.description

class Photo(models.Model):
	photo = models.ImageField(upload_to='moment_images', blank=True)
	moment = models.OneToOneField(Moment)
	#base64_image_str = models.TextField()

	def __str__(self):
		return self.photo.url

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	picture = models.ImageField(upload_to='profile_images', blank=True)
	friends = models.ManyToManyField('self')

	def __str__(self):
		return self.user.username