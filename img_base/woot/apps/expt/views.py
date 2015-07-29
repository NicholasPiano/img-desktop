# woot.apps.expt.views

# django
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.views.generic import View

# local

# util

### Views

# methods
def my_view(request):
    if request.method == 'GET':
        # <view logic>
        return HttpResponse('result')

# classes
### https://docs.djangoproject.com/en/1.7/topics/class-based-views/intro/
class MyView(View):
    def get(self, request):
        # <view logic>
        return HttpResponse('result')
