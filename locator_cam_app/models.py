from django.db import models
from django.contrib.auth.models import User
import hashlib




class UserProfile(models.Model):
	user = models.OneToOneField(User)
	picture = models.ImageField(upload_to='profile_images', blank=True, null=True)
	friends = models.ManyToManyField('self')

	def __str__(self):
		return self.user.username

class Channel(models.Model):
	name = models.CharField(max_length=256)
	description = models.TextField()
	time_created = models.DateTimeField(auto_now_add=True)
	user_created = models.ForeignKey(UserProfile)
	administrators = models.ManyToManyField(UserProfile, related_name='admin_channels')
	members = models.ManyToManyField(UserProfile, related_name='membership_channels')
	is_private_channel = models.BooleanField(default=True)

	def __str__(self):
		return '{0:s} ({1:s})'.format(self.name, self.user_created.user.username)


class Moment(models.Model):
	description = models.TextField(default='', blank=True, null=True)
	latitude = models.FloatField(blank=True, null=True)
	longitude = models.FloatField(blank=True, null=True)
	user = models.ForeignKey(User)
	pub_time_interval = models.FloatField(db_index=True, blank=True, null=True)
	pub_time = models.DateTimeField(db_index=True, auto_now_add=True, blank=True, null=True)
	channel = models.ForeignKey(Channel, blank=True, null=True)

	class Meta:
		ordering = ['-pub_time_interval']

	def __str__(self):
		return '%s: %s' % (self.user.username, self.description)

class MomentPhoto(models.Model):
	moment = models.OneToOneField(Moment)
	photo_base64 = models.TextField(blank=True, null=True)

	def __str__(self):
		return '{username: %s, description: %s}' % (self.moment.user.username, self.moment.description)

class MomentThumbnail(models.Model):
	moment = models.OneToOneField(Moment)
	thumbnail_base64 = models.TextField(blank=True, null=True)

	def __str__(self):
		return '{username: %s, description: %s}' % (self.moment.user.username, self.moment.description)
