from django.urls import path
from . import views

app_name = 'glossario'

urlpatterns = [
    path('', views.index, name='index'),
]
