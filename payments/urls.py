from django.urls import path
from .views import *

urlpatterns = [
    path("",HomepageView.as_view(),name="home"),
    path("charge/",ChargeView,name="charge"),
    path("charge_all/",Charge_allView,name="charge_all"),
    path("bill/",BillDetails.as_view(),name="bill"),
    path("login/",LoginView.as_view(),name="login"),
    path("createuser/",CreateUserView.as_view(),name="createuser"),
    path("category/",CategoryView.as_view(),name="category"),
    path("product/",ProductView.as_view(),name="product"),
    path("bank-details/",SellerBankDetailsView.as_view(),name="bank-details"),
    path("cart/",CartView.as_view(),name="cart"),
    path("order/",OrderView.as_view(),name="order"),
    path("delivery/",DeliveryDetailsView.as_view(),name="delivery"),
    path("update-category/<int:id>/",CategoryView.as_view(),name="update-category"),
    path("update-product/<int:id>/",ProductView.as_view(),name="update-product"),
    path("update-bank-details/<int:id>/",SellerBankDetailsView.as_view(),name="update-bank-details"),
    path("update-cart/<int:id>/",CartView.as_view(),name="update-cart"),
    path("update-delivery/<int:id>/",DeliveryDetailsView.as_view(),name="update-delivery"),
    path('verify-phone/', VerifyPhoneNumberView.as_view(), name='verify_phone'),

]
