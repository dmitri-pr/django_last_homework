from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.decorators.cache import cache_page

from .views import (ShopIndexView, GroupListView, ProductDetailView,
                    ProductListView, OrderListView, OrderDetailView,
                    ProductCreateView, ProductUpdateView, ProductDeleteView,
                    OrderCreateView, OrderUpdateView, OrderDeleteView,
                    ProductDataExportView, OrderDataExportView,
                    ProductViewSet, OrderViewSet, LatestProductsFeed,
                    UserOrdersListView, ExportUserOrdersView)

app_name = 'shopapp'

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('orders', OrderViewSet)

urlpatterns = [
    # path('', cache_page(60 * 3)(ShopIndexView.as_view()), name='index'),
    path('', ShopIndexView.as_view(), name='index'),
    path('api/', include(router.urls)),
    path('groups/', GroupListView.as_view(), name='groups_list'),
    path('products/', ProductListView.as_view(), name='products_list'),
    path('products/export/', ProductDataExportView.as_view(), name='products_export'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_details'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/archive/', ProductDeleteView.as_view(), name='product_delete'),
    path('orders/', OrderListView.as_view(), name='orders_list'),
    path('orders/export/', OrderDataExportView.as_view(), name='orders_export'),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_details'),
    path('orders/<int:pk>/update/', OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),
    path('products/latest/feed/', LatestProductsFeed(), name='products-feed'),
    path('users/<int:user_id>/orders/', UserOrdersListView.as_view(), name='user_orders'),
    path('users/<int:user_id>/orders/export/', ExportUserOrdersView.as_view(), name='export_user_orders'),
]
