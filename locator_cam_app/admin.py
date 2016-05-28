from django.contrib import admin
from locator_cam_app.models import Photo, Moment, UserProfile

# Register your models here.
admin.site.register(Photo)
admin.site.register(Moment)
admin.site.register(UserProfile)