from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:list_id>/', views.listitems, name='list_items'),
]
