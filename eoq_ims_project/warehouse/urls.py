# warehouse/urls.py
from django.urls import path
from . import views

app_name = 'warehouse'

urlpatterns = [
    path('list/', views.warehouse_list, name='warehouse_list'),  
    path('<int:pk>/', views.warehouse_detail, name='warehouse_detail'),
    path('create/', views.warehouse_create, name='warehouse_create'),
    path('<int:pk>/update/', views.warehouse_update, name='warehouse_update'),
    path('<int:pk>/delete/', views.warehouse_delete, name='warehouse_delete'),
]