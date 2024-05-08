from rest_framework.permissions import BasePermission, IsAuthenticated

from restaurantAPI.models import OrderItem

MANAGER_METHODS = ('POST', 'PUT', 'DELETE')
SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


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


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated
        )


class IsManagerOrCustomerReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in MANAGER_METHODS:
            if bool(request.user and
                    request.user.is_staff and
                    request.user.is_superuser and
                    request.user.groups.filter(name='manager').exists()):
                return True
            return False
        elif request.method in SAFE_METHODS:
            is_authenticated = IsAuthenticated()
            return is_authenticated.has_permission(request, view)
        else:
            return False


class IsCustomerOrManagerReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            if bool(request.user and
                    request.user.groups.filter(name='customer').exists()):
                return True
            return False
        elif request.method == 'GET':
            is_authenticated = IsAuthenticated()
            return is_authenticated.has_permission(request, view)
        else:
            return False
