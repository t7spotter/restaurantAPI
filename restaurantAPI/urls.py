from django.urls import path

from .views import ListMenuItems, ManagerGroupManagement, DeliveryGroupManagement

urlpatterns = [
    path('menu-items', ListMenuItems.as_view()),
    path('menu-items/<int:pk>', ListMenuItems.as_view()),


    path('groups/manager/users', ManagerGroupManagement.as_view()),
    path('groups/manager/users/<int:pk>', ManagerGroupManagement.as_view()),

    path('/api/groups/delivery-crew/users', DeliveryGroupManagement.as_view()),
    path('/api/groups/delivery-crew/users/<int:pk>', DeliveryGroupManagement.as_view()),
]