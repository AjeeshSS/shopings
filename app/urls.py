from django.urls import path
from app import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home),
    path('home', views.home, name='home'),
    path('user_registration/', views.UserRegistrationView.as_view(), name='user_registration'),
    path('user_login/', views.user_login.as_view(), name='user_login'), 
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('logout', views.logout_page, name='logout'),

    path('addaddress/', views.AddressView.as_view(), name='addaddress'),
    path('checkout_add_address/', views.checkout_add_address, name='checkout_add_address'),
    path('address/', views.address, name='address'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('edit_address/', views.edit_address, name='edit_address'),
    path('address/delete_address', views.delete_address, name='delete_address'),

    path('otp_page', views.otp_page, name='otp_page'),
    path('product-detail/', views.ProductDetailView.as_view(), name='product-detail'),
    path('buy_now/', views.buy_now, name='buy_now'),
    path('buynow_add_address/', views.buynow_add_address, name='buynow_add_address'),
    path('orders/', views.orders, name='orders'),

    path('mobile/', views.mobile, name='mobile'),
    path('mobiledata/<slug:data>', views.mobile, name='mobiledata'),

    path('lap/', views.lap, name='lap'),
    path('lapdata/<slug:data>', views.lap, name='lapdata'),

    path('cart', views.show_cart, name='cart'),
    path('add_to_cart', views.add_to_cart, name='add_to_cart'),
    path('pluscart', views.plus_cart),
    path('minuscart', views.minus_cart),
    path('removecart', views.remove_cart, name='removecart'),

    path('checkout/', views.checkout, name='checkout'),
    path('paymentdone/', views.payment_done, name='paymentdone'),
    path('buynowpaymentdone/', views.buynowpayment_done, name='buynowpaymentdone'),
    path('cancel_product/', views.cancel_product, name='cancel_product'),
    path('invoice/', views.invoice, name='invoice'),
    path('download/', views.download, name='download'),
    path('download_excel/', views.download_excel, name='download_excel'),
    path('return_product/', views.return_product, name='return_product'),
    
    path('apply_coupon', views.apply_coupon, name='apply_coupon'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
