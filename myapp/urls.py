from django.urls import path
from .views import user_dashboard, edit_preferences, home
from django.contrib.auth import views as auth_views
from . import views
from .wallet.wallet import wrap_wallet

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', user_dashboard, name='dashboard'),
    path('edit_preferences/', edit_preferences, name='edit_preferences'),
    path('register/', views.register, name='register'),
    path('', home, name='home'),
    path('portfolio/', wrap_wallet, name='portfolio'),
]
