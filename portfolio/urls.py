from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('<slug:slug>/', views.detalhe, name='detalhe'),
]
