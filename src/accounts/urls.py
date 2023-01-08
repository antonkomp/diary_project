from django.urls import path
from django.conf.urls import url
from .views import main, login_user, logout, registr_user, register_confirm, profile, edit, \
    account, message, message_details, send_message, delete_message, open_image_message, api, APIUser, APIUserEdit,\
    APIProfile, APIProfileEdit, APIAccount, validate_username


urlpatterns = [
    path('', main, name='main'),
    path('login/', login_user, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', registr_user, name='register'),
    url(r'^register/confirm/(?P<key>[0-9a-f]{32})/$', register_confirm, name='register_confirm'),
    path('profile/', profile, name='profile'),
    path('edit/', edit, name='edit'),
    path('account_type/', account, name='account'),
    path('my_messages/', message, name='my_messages'),
    path('message_details/<int:messages_id>/', message_details, name='message_details'),
    path('send_message/', send_message, name='send_message'),
    path('delete_message/<int:message_id>/', delete_message, name='delete_message'),
    path('open_image_message/<int:message_id>/', open_image_message, name='open_image_message'),
    path('api/', api, name='api'),
    path('api/user/get/', APIUser.as_view()),
    path('api/user/edit/', APIUserEdit.as_view()),
    path('api/profile/get/', APIProfile.as_view()),
    path('api/profile/edit/', APIProfileEdit.as_view()),
    path('api/account/', APIAccount.as_view()),
    path('validate_username', validate_username, name='validate_username'),
    ]

