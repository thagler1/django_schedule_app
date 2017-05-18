from django.conf.urls import url
from . import views
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'adduser', views.create_user, name ="adduser"),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^user/(?P<calmonth>[0-9]{2})', views.user_page, name ='userpage'),
    url(r'^user/', views.user_page, name ='userpage'),
    url(r'^pto', views.controller_pto_form, name ='pto'),
    url(r'^unapproved_pto', views.unnaproved_pto, name ='unapproved_pto'),
    url(r'^shift_supervisor_console', views.supervisors_console, name ='supervisor_console'),
    url(r'^debug',views.debugpage,name='debug'),
    url(r'^test', views.add_console,name='test')




    ]

