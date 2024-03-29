from django.urls import path

from .views import ListMenuItems, ManagerGroupManagement, DeliveryGroupManagement, UserCartManager, OrderManagement, OrderDeliveryStatusManagement, ListCategory


urlpatterns = [
    path('menu-items', ListMenuItems.as_view()),
    path('menu-items/<int:pk>', ListMenuItems.as_view()),


    path('category', ListCategory.as_view()),
    path('category/<int:pk>', ListCategory.as_view()),

    path('groups/manager/users', ManagerGroupManagement.as_view()),
    path('groups/manager/users/<int:pk>', ManagerGroupManagement.as_view()),

    path('groups/delivery-crew/users', DeliveryGroupManagement.as_view()),
    path('groups/delivery-crew/users/<int:pk>', DeliveryGroupManagement.as_view()),


    path('cart/menu-items', UserCartManager.as_view()),
    path('cart/menu-items/<int:pk>', UserCartManager.as_view()),


    path('orders', OrderManagement.as_view()),
    path('orders/<int:pk>', OrderManagement.as_view()),

    path('delivery', OrderDeliveryStatusManagement.as_view()),
    path('delivery/<int:pk>', OrderDeliveryStatusManagement.as_view()),

]
