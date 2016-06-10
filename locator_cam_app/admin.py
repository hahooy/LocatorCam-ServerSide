from django.contrib import admin
from locator_cam_app.models import MomentPhoto, Moment, UserProfile, MomentThumbnail

# Register your models here.
admin.site.register(MomentPhoto)
admin.site.register(Moment)
admin.site.register(UserProfile)
admin.site.register(MomentThumbnail)