from django.urls import path
from blog import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('', views.index, name='index'),
    path('article/<int:aid>', views.article, name='article'),
    path('type/<int:tid>', views.posts_type, name='posts_type'),
    path('time/<int:year>/<int:month>', views.posts_time, name='posts_time'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('like_change', views.like_change, name='like_change'),
    path('update_comment', views.update_comment, name='update_comment'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
]
