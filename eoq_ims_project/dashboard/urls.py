# dashboard/urls.py
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('inventory/', views.inventory_overview, name='inventory'),
    path('procurement/', views.procurement_dashboard, name='procurement'),
    path('eoq/', views.eoq_dashboard, name='eoq'),
    path('warehouse/', views.warehouse_dashboard, name='warehouse'),
    path('demand/', views.demand_analysis, name='demand'),
]

