from django.urls import path
from . import views

urlpatterns = [
    path('',views.SignupPage,name='signup'),
    path('login/',views.LoginPage,name='login'),
    path('index/', views.index, name='index'),
    path('generate-question/', views.generate_question_view, name='generate-question'), 
    path('check-answer', views.check_answer_view, name='check-answer'),
    path('logout/',views.LogoutPage,name='logout'),
    path('homepage/',views.HomePage,name='homepage'),


]
