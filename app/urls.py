from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name="home"),
    path('cart/',views.cart, name="cart"),
    path('checkout/',views.checkout, name="checkout"),
    path('update_item/',views.updateItem, name="update_item"),
    path('register/',views.register, name="register"),
    path('login/',views.loginPage, name="login"),
    path('logout/',views.logoutPage, name = "logout"),
    path('search/',views.search, name="search"),
    path('category/',views.category,name='category'),
    path('order_info/', views.showOrderInfo, name='order_info_default'),
    path('order_info/<slug:slug>/', views.showOrderInfo, name='order_info'),
    path('order_manage/',views.manageOrder, name='order_manage_default'),
    path("order_manage/<slug:slug>", views.manageOrder, name="order_manage"),
    path('product_manage',views.manageProduct, name='product_manage'),
    path('staff_manage/',views.manageStaff,name='staff_manage'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('product_modify/<int:product_id>/',views.modifyProduct, name='product_modify'),
    path('product_add', views.addProduct, name='product_add'),
    path("add_new_category/", views.addNewCategory, name="add_new_category"),
    path('about_us/',views.aboutUs,name='about_us'),
]