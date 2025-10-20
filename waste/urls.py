from django.urls import path
from . import views



urlpatterns = [
    # Main views with your desired URL names
    path('', views.list_waste, name='waste_list'),
    path('create/', views.create_waste, name='waste_listing_create'),
    path('update/<int:pk>/', views.update_waste, name='waste_update'),
    path('delete/<int:pk>/', views.delete_waste, name='waste_delete'),
    
    # Additional views
    path('my-listings/', views.waste_listings, name='waste_listings'),
    path('<int:pk>/', views.waste_listing_detail, name='waste_detail'),
    path('public/', views.public_listings, name='public_listings'),
]
