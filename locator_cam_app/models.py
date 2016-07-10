from datetime import datetime

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

class Request(models.Model):
	requester = models.ForeignKey(User)
	time_created = models.DateTimeField(auto_now_add=True)
	request_message = models.TextField(blank=True, null=True)

class FriendRequest(Request):
	requestee = models.ForeignKey(User)

	def save(self, *args, **kwargs):
		if self.requester == self.requestee:
			# cannot send a friend request to self
			return
		else:
			try:
				existing_request = FriendRequest.objects.get(requester=self.requester, requestee=self.requestee)
			except Exception as e:
				existing_request = None
			if existing_request:
				# this friend request exists, just update fields
				existing_request.time_created = datetime.utcnow()
				existing_request.request_message = self.request_message
				existing_request.save()
			else:
				super(FriendRequest, self).save(*args, **kwargs)

	def __str__(self):
		return '"%s" requests to become a friend of "%s"' % (self.requester.username, self.requestee.username)

class ChannelRequest(Request):
	channel = models.ForeignKey(Channel)

	def __str__(self):
		return '"%s" requests to join channel "%s"' % (self.requester.username, self.channel.name)

class ChannelInvitation(Request):
	invitee = models.ForeignKey(User)
	channel = models.ForeignKey(Channel)

	def save(self, *args, **kwargs):
		if self.requester == self.invitee:
			# cannot send a channel invitation to self
			return
		else:
			super(ChannelInvitation, self).save(*args, **kwargs)

	def __str__(self):
		return '%s invites %s to join channel: %s' % (self.requester.username, self.invitee.username, self.channel.name)

class Notification(models.Model):
	receiver = models.ForeignKey(User)
	message = models.TextField()

	def __str__(self):
		return 'Notify "%s"' % (self.receiver.username)

