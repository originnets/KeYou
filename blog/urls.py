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
    path('change_nickname', views.change_nickname, name='change_nickname'),
    path('bind_email', views.bind_email, name='bind_email'),
    path('send_verification_code', views.send_verification_code, name='send_verification_code'),
    path('change_password', views.change_password, name='change_password'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('logout', views.logout, name='logout'),
]
