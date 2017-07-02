from django.conf.urls import url
from . import views
from .sms import incoming


urlpatterns = [
    url(r'^$', views.user_login, name='index'),
    url(r'adduser', views.create_user, name ="adduser"),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^user/(?P<calmonth>[0-9]{2})', views.user_page, name ='userpage'),
    url(r'^user/', views.user_page, name ='userpage'),
    url(r'^pto', views.controller_pto_form, name ='pto'),
    url(r'^unapproved_pto', views.unnaproved_pto, name ='unapproved_pto'),
    url(r'^shift_supervisor_console', views.supervisors_console, name ='supervisor_console'),
    url(r'^add_console', views.add_console,name='test'),
    url(r'^schedule_coverage/(?P<pto_id>[0-9]+)', views.schedule_coverage, name=''),
    url(r'^unapproved/(?P<console>[A-z]+\s?[A-z]+)', views.console_approval, name=''),
    url(r'^approved_pto_list', views.approved_pto),
    url(r'^logout/', views.user_logout, name='logout'),
    url(r'^twilio_response_2147270215', incoming.receive_response ),
    url(r'^console_calendars', views.console_schedule_menu),
    url(r'^ajax_schedule', views.ajax_schedule),
    url(r'^ajax_user_pto_report', views.ajax_user_pto_table),





    ]

