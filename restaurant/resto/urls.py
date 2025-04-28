from django.urls import path
from . import views

app_name = 'resto'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('commandes/', views.CommandesView.as_view(), name='commandes'),
    path('menu/', views.MenuListView.as_view(), name='menu_list'),
    path('menu/<str:category>/', views.MenuListView.as_view(), name='menu_list_category'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('basket/add/<int:item_id>/', views.add_to_basket, name='add_to_basket'),
    path('basket/', views.basket_view, name='basket'),
    path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('order/delete/<int:order_id>/', views.delete_order, name='delete_order'),


]
"""

    path('menu/add', views.MenuCreateView.as_view(), name='menu_create'),
    path('menu/edit/<int:pk>/', views.MenuUpdateView.as_view(), name='menu_update'),
    path('menu/delete/<int:pk>/', views.MenuDeleteView.as_view(), name='menu_delete'),

"""