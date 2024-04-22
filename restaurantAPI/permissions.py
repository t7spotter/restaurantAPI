from rest_framework.permissions import BasePermission


class IsManager(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff and request.user.is_superuser)


class IsDeliveryCrew(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='delivery'))


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='customer'))
