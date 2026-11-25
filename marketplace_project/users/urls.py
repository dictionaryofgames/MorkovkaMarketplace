from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('vendor/create/', views.create_vendor, name='create_vendor'),
    path('vendor/<slug:slug>/', views.VendorDetailView.as_view(), name='vendor_detail'),
]
