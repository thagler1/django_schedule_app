from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'deskschedule', views.console_schedule_menu, name ='deskschedule'),
    url(r'adduser', views.lexusadduser, name ="adduser"),
    url(r'^login/$', views.user_login, name='login')
    ]