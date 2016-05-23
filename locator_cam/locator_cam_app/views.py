from django.shortcuts import render

# Create your views here.

def index(request):
	return render(request, 'locator_cam_app/index.html', {})