import django.urls 

from . import views

urlpatterns = [
    django.urls.path('', views.index, name='index'),
]