from django.urls import path
from adminapp import views

urlpatterns = [
    path('admin_login', views.admin_login, name='admin_login'),
    path('admin/admin_logout', views.admin_logout, name='admin_logout'),
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('sales_report', views.sales_report, name='sales_report'),
    
    path('admin_users', views.admin_users, name='admin_users'),
    path('userblock', views.userblock, name='userblock'),

    path('admin_products', views.admin_products, name='admin_products'),
    path('add_new_product', views.add_new_product, name='add_new_product'),
    path('edit_product/<int:id>', views.edit_product, name='edit_product'),
    path('delete_product/<int:id>', views.delete_product, name='delete_product'),

    path('admin_orders', views.admin_orders, name='admin_orders'),
    path('edit_status', views.edit_status, name='edit_status'),

    path('admin_category', views.admin_category, name='admin_category'),
    path('add_new_category', views.add_new_category, name='add_new_category'),
    path('edit_category/<int:id>', views.edit_category, name='edit_category'),
    path('delete_category/<int:id>', views.delete_category, name='delete_category'),
    
    path('admin_brand', views.admin_brand, name='admin_brand'),
    path('add_new_brand', views.add_new_brand, name='add_new_brand'),
    path('edit_brand/<int:id>', views.edit_brand, name='edit_brand'),
    path('delete_brand/<int:id>', views.delete_brand, name='delete_brand'),
    
    path('admin_coupon', views.admin_coupon, name='admin_coupon'),
    path('add_new_coupon', views.add_new_coupon, name='add_new_coupon'),
    path('edit_coupon/<int:id>', views.edit_coupon, name='edit_coupon'),
    path('delete_coupon/<int:id>', views.delete_coupon, name='delete_coupon'),
    
    path('admin_colours', views.admin_colours, name='admin_colours'),
    path('add_new_colours', views.add_new_colours, name='add_new_colours'),
    path('edit_colours/<int:id>', views.edit_colours, name='edit_colours'),
    path('delete_colours/<int:id>', views.delete_colours, name='delete_colours'),
    
    path('admin_Colour_combination', views.admin_Colour_combination, name='admin_Colour_combination'),
    path('add_new_colour_combination', views.add_new_colour_combination, name='add_new_colour_combination'),
    path('edit_colour_combination/<int:id>', views.edit_colour_combination, name='edit_colour_combination'),
    path('delete_colour_combination/<int:id>', views.delete_colour_combination, name='delete_colour_combination'),
    
    ]