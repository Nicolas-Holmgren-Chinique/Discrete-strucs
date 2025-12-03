from django.urls import path
from . import views


"""
URL patterns for the home app and being able to route to the home view and calculate_route view
"""
urlpatterns = [
    path('', views.home, name='home'),
    path('calculate_route/', views.calculate_route, name='calculate_route'),
]
