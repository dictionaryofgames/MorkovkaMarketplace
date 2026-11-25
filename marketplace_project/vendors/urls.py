from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('dashboard/', views.vendor_dashboard, name='dashboard'),
    # Products CRUD
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    # Orders
    path('orders/', views.VendorOrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/status/', views.VendorOrderUpdateView.as_view(), name='order_update'),
]
