from django.db import models
from django.contrib.auth.models import User
import hashlib



class Moment(models.Model):
	description = models.TextField(default='', blank=True, null=True)
	latitude = models.FloatField()
	longitude = models.FloatField()
	user = models.ForeignKey(User)
	#photo = models.OneToOneField(Photo)
	#thumbnail = models.ImageField(upload_to='thumbnail_images', blank=True)
	thumbnail_base64 = models.TextField(blank=True, null=True)
	pub_time_interval = models.FloatField(db_index=True, blank=True, null=True)
	pub_time = models.DateTimeField(db_index=True, auto_now_add=True, blank=True, null=True)

	class Meta:
		ordering = ['-pub_time_interval']

	def __str__(self):
		return '%s: %s' % (self.user.username, self.description)

class Photo(models.Model):
	#photo = models.ImageField(upload_to='moment_images', blank=True)
	moment = models.OneToOneField(Moment)
	photo_base64 = models.TextField(blank=True, null=True)

	def __str__(self):
		return '{username: %s, description: %s}' % (self.moment.user.username, self.moment.description)

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	picture = models.ImageField(upload_to='profile_images', blank=True)
	friends = models.ManyToManyField('self')

	def __str__(self):
		return self.user.username