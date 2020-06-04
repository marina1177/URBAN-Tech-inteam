from django.urls import path
from . import views

urlpatterns = [
    path('', views.contractor_view),
]
