from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('sobre/', views.sobre, name='sobre'),
    path('servicos/', views.servicos, name='servicos'),
    path('hardware/', views.hardware, name='hardware'),
    path('privacidade/', views.privacidade, name='privacidade'),
    path('contato/', views.contato, name='contato'),
]
