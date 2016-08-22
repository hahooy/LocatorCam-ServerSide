from datetime import datetime
import json
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "locator_cam.settings")

import django
django.setup()
from django.contrib.auth.models import User

from locator_cam_app.models import Moment, MomentPhoto, MomentThumbnail, UserProfile


data = json.load(open('fishboard-export.json'))

# Create a new user
user = User(username='JestersHK1', password='******', email='unknow@gmail.com')
user.save()
user_profile = UserProfile()
user_profile.user = user
user_profile.save()


for key, val in data['dev']['moments'].items():
	print(key)
	moment = Moment()
	moment.description = val.get('description')
	moment.latitude = val.get('latitude')
	moment.longitude = val.get('longitude')
	moment.user = user
	moment.pub_time_interval = val.get('time')
	moment.pub_time = datetime.now()
	moment.channel = None
	moment.save()

	photo = MomentPhoto()
	photo.photo_base64 = data['dev']['photos'][val.get('photoReferenceKey')]
	photo.moment = moment
	photo.save()

	thumbnail = MomentThumbnail()
	thumbnail.thumbnail_base64 = val.get('thumbnailBase64')
	thumbnail.moment = moment
	thumbnail.save()



