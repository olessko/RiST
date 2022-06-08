# from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import user_login, logout_view

app_name = 'accounts'

urlpatterns = [

    path('login/', user_login, name='login'),
    path('logout/', logout_view, name='logout'),

]
