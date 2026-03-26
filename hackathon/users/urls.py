from django.contrib.auth import views as auth_views

import django.urls
import users.views
urlpatterns = [
    django.urls.path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    django.urls.path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    django.urls.path('register/', users.views.register, name='register'),
]