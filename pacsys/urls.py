from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *


urlpatterns = [
    path('', index, name='index'),
    path('details/', parcel_details, name='parcel_details'),
    path('track/', track, name='track_parcel'),
    path('admin/', admin_panel, name='admin_panel'),
    path('update_parcel_status/', update_parcel_status, name='update_parcel_status'),
    path('parcel/search/', parcel_search, name='parcel_search'),
    path('register_parcel/', register_parcel, name='register_parcel'),
    path('signup/', signup, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('confirm_email/<str:uidb64>/<str:token>/', confirm_email, name='confirm_email'),
    path('email_confirmation/', email_confirmation, name='email_confirmation'),
    path('email_confirmed/', email_confirmed, name='email_confirmed'),
    path('email_confirmation_invalid/', email_confirmation_invalid, name='email_confirmation_invalid'),
    path('login/', login_view, name='login'),
    path('home/', home, name='home'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="password_reset.html"), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="reset.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), name='password_reset_complete'),
]
