from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_user, name='all_user'),
    path('register/', views.RegisterView.as_view(), name='register'),
]
