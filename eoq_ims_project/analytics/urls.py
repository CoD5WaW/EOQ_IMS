# analytics/urls.py
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # EOQ Parameters routes
    path('eoq-parameters/', views.eoq_parameters_selection, name='eoq_parameters_selection'),  # New route for product selection
    path('product/<int:product_id>/eoq/', views.eoq_parameters, name='eoq_parameters'),
    path('eoq-calculation/', views.eoq_calculation, name='eoq_calculation'),
    path('eoq-parameters/list/', views.eoq_parameters_list, name='eoq_parameters_list'),
    
    # Demand History routes
    path('demand/add/', views.add_demand_history, name='add_demand_history'),
    path('product/<int:product_id>/demand/add/', views.add_demand_history, name='add_product_demand'),
    path('demand/', views.demand_history_list, name='demand_history_list'),
    path('demand/upload/', views.bulk_demand_upload, name='bulk_demand_upload'),
    
    # Analysis routes
    path('analysis/', views.inventory_analysis, name='inventory_analysis'),
    path('api/demand-chart/<int:product_id>/', views.demand_chart_data, name='demand_chart_data'),
]