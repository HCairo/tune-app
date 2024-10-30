from django.urls import path
from tune.views import home, login, logout, callback, user

urlpatterns = [
    path('', home, name='home'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('callback/', callback, name='callback'),
    path('user/', user, name='user'),
]
