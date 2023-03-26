from django.urls import path
from django.conf.urls import url
from .views import main, login_user, logout, registr_user, register_confirm, profile, edit, \
    account, api, APIUser, APIUserEdit,\
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
    path('api/', api, name='api'),
    path('api/user/get/', APIUser.as_view()),
    path('api/user/edit/', APIUserEdit.as_view()),
    path('api/profile/get/', APIProfile.as_view()),
    path('api/profile/edit/', APIProfileEdit.as_view()),
    path('api/account/', APIAccount.as_view()),
    path('validate_username', validate_username, name='validate_username'),
    ]

