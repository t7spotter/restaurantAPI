from rest_framework.permissions import BasePermission

from restaurantAPI.models import OrderItem


class IsManager(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff and request.user.is_superuser)


class IsDeliveryCrew(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='delivery'))


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='customer'))


class IsCustomerAndHasBoughtItem(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            is_customer = IsCustomer()
            return is_customer.has_permission(request, view)
        elif request.method == 'POST':
            if request.user.is_authenticated:
                item_id = view.kwargs.get('pk')
                has_ordered_item = OrderItem.objects.filter(order__user=request.user, menuitem=item_id).exists()
                return has_ordered_item
            return False
        else:
            return False
