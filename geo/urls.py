from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('regions/', views.region_list, name='region_list'),
    path('regions/<int:pk>/', views.region_detail, name='region_detail'),
    path('objects/', views.object_list, name='object_list'),
    path('objects/<int:pk>/', views.object_detail, name='object_detail'),
    path('attractions/', views.attraction_list, name='attraction_list'),
    path('attractions/<int:pk>/', views.attraction_detail, name='attraction_detail'),
    path('map/', views.map_page, name='map_page'),
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quizzes/<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('quizzes/<int:pk>/result/', views.quiz_result, name='quiz_result'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
]
