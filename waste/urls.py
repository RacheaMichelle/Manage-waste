from django.urls import path
from . import views



urlpatterns = [
    path('', views.waste_listings, name='waste_list'), 
    path('create/', views.create_waste_listing, name='waste_create'),
    path('', views.waste_listings, name='waste_listings'),
    path('<int:pk>/', views.waste_listing_detail, name='waste_detail'),
    path('<int:pk>/update/', views.update_waste_listing, name='waste_update'),
    path('<int:pk>/delete/', views.delete_waste_listing, name='waste_delete'),
    path('public/', views.public_listings, name='public_listings'),
]
