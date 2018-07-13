from django.urls import path
from blog import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('article', views.article, name='article'),
]