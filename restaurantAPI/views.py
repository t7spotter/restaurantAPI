import random
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import MenuItem, Cart, OrderItem
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer
from .permissions import IsManager


class ListMenuItems(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk=None):
        if pk:
            queryset = get_object_or_404(MenuItem, pk=pk)
            ser = MenuItemSerializer(queryset)
            return Response(ser.data, status=status.HTTP_200_OK)
        else:
            queryset = MenuItem.objects.all()
            ser = MenuItemSerializer(queryset, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)

    def post(self, request: Request, pk=None):
        if pk:
            return Response({"message": "The post method has not to get pk argument"},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.user.groups.filter(name='manager').exists():  # only manger group members can use post method
            ser = MenuItemSerializer(data=request.data)
            if ser.is_valid():
                ser.save()
                return Response(ser.data, status.HTTP_201_CREATED)
            else:
                return Response(ser.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You have not permission for this action"}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request: Request, pk):
        if request.user.groups.filter(name='manager').exists():  # only manger group members can use put method
            try:
                queryset = get_object_or_404(MenuItem, pk=pk)
                ser = MenuItemSerializer(queryset, data=request.data)
            except MenuItem.DoesNotExist:
                return Response({"message": "This menu item does not exists"}, status=status.HTTP_400_BAD_REQUEST)
            if ser.is_valid():
                ser.save()
                return Response([{"message": f"'{queryset.title}' updated"}, ser.data], status=status.HTTP_200_OK)
        else:
            return Response({"message": "You have not permission for this action"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request: Request, pk):
        if request.user.groups.filter(name='manager').exists():  # only manger group members can use delete method
            try:
                queryset = get_object_or_404(MenuItem, pk=pk)
            except MenuItem.DoesNotExist:
                return Response({"message": "This menu item does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                queryset.delete()
                return Response({"message": f"'{queryset.title}' Deleted"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "You have not permission for this action"},
                            status=status.HTTP_403_FORBIDDEN)


class ManagerGroupManagement(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsManager]

    def get(self, request: Request, pk=None):
        if pk:
            try:
                queryset = User.objects.filter(groups__name='manager').get(pk=pk)
                ser = UserSerializer(queryset)
                return Response(ser.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"message": "This manager user does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            queryset = User.objects.filter(groups__name='manager')
            ser = UserSerializer(queryset, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)

    def post(self, request: Request):
        user = get_object_or_404(User, username=request.data.get('username'))
        managers = get_object_or_404(Group, name='manager')

        user.groups.add(managers)
        return Response({"message": f"'{user}' added to the manager group"}, status=status.HTTP_201_CREATED)

    def delete(self, request: Request, pk):
        user = get_object_or_404(User, pk=pk)
        managers = get_object_or_404(Group, name='manager')

        user.groups.remove(managers)
        return Response({"message": f"'{user}' deleted from the manager group"}, status=status.HTTP_204_NO_CONTENT)


class DeliveryGroupManagement(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsManager]

    def get(self, request: Request, pk=None):
        if pk:
            try:
                queryset = User.objects.filter(groups__name='delivery').get(pk=pk)
                ser = UserSerializer(queryset)
                return Response(ser.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"message": "This delivery user does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            queryset = User.objects.filter(groups__name='delivery')
            ser = UserSerializer(queryset, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)

    def post(self, request: Request):
        user = get_object_or_404(User, username=request.data.get('username'))
        delivery_crews = get_object_or_404(Group, name='delivery')

        user.groups.add(delivery_crews)
        return Response({"message": f"'{user}' added to the delivery group"}, status=status.HTTP_201_CREATED)

    def delete(self, request: Request, pk):
        user = get_object_or_404(User, pk=pk)
        managers = get_object_or_404(Group, name='delivery')

        user.groups.remove(managers)
        return Response({"message": f"'{user}' deleted from the delivery group"}, status=status.HTTP_204_NO_CONTENT)


class UserCartManager(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        if request.user.groups.filter(name='manager').exists():
            queryset = Cart.objects.order_by('user').all()
            ser = CartSerializer(queryset, many=True)

            # --------------------------------------------------------------------------------------------------
            # all_items_in_single_cart = set(user.user_id for user in queryset)
            # carts_by_each_user = [Cart.objects.filter(user=cart) for cart in all_items_in_single_cart]

            # for cart in carts_by_each_user:
            #     user_total_cart_price = 0
            #     ii = []
            #     for item in cart:
            #         user_total_cart_price += item.price
            #         ii.append(float(user_total_cart_price))
            #
            # listt = [ser.data[4]['price']]
            # print(listt)
            # print(dir(ser.data))
            # -------------------------------------------------------------------------------------------------
            return Response(ser.data, status=status.HTTP_200_OK)

        elif request.user.groups.filter(name='customer').exists():
            queryset = Cart.objects.filter(user=request.user)
            ser = CartSerializer(queryset, many=True)

            total_order_price = self.get_total_price(queryset)
            return Response([{"items in your cart": ser.data}, {"total order price": total_order_price}],
                            status=status.HTTP_200_OK)

    def post(self, request: Request):
        if request.user.groups.filter(name='customer').exists():
            try:
                menuitem_id = request.data['menuitem']
                quantity = request.data['quantity']
            except KeyError:
                return Response(
                    [{"message": "please send valid data"}, {"menuitem": "menuitem id", "quantity": "int: how many?"}],
                    status=status.HTTP_400_BAD_REQUEST)
            try:
                menu_item = get_object_or_404(MenuItem, pk=menuitem_id)
            except (MenuItem.DoesNotExist, ValueError):
                return Response({'error': 'Menu item not found.'}, status=status.HTTP_404_NOT_FOUND)

            user_cart = Cart.objects.filter(user=request.user)
            if user_cart.filter(menuitem=menuitem_id).count() != 0:
                get_menu_item_in_current_cart = get_object_or_404(Cart, user=request.user, menuitem=menuitem_id)
                get_menu_item_in_current_cart.quantity += quantity
                new_quantity_price = quantity * menu_item.price
                get_menu_item_in_current_cart.price += new_quantity_price
                get_menu_item_in_current_cart.save()

                ser = CartSerializer(get_menu_item_in_current_cart)
                return Response({"message": "ok", "item": ser.data}, status=status.HTTP_200_OK)

            elif user_cart.filter(menuitem=menuitem_id).count() == 0:
                unit_price = menu_item.price
                price = quantity * unit_price

                cart_data = {
                    "user": request.user.id,
                    "menuitem": menu_item.id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "price": price
                }

                ser = CartSerializer(data=cart_data)
                if ser.is_valid():
                    ser.save()
                    return Response(ser.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'User is not in the "customer" group.'}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request):  # TODO: Add pk parameter
        if request.user.groups.filter(name="customer"):
            queryset = Cart.objects.filter(user=request.user)
            queryset.delete()
            return Response({"messages": "Cart cleared"}, status=status.HTTP_204_NO_CONTENT)

    def get_total_price(self, items):
        total_order_price = 0
        for item in items:
            total_order_price += item.price
        return total_order_price


class OrderManagement(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart_items = Cart.objects.filter(user=request.user).count()
        if cart_items == 0:
            return Response({"messages": "No items in your cart"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user_cart = Cart.objects.filter(user=request.user)
            total_cart_price = Cart.get_total_price(user_cart)

            delivery = User.objects.filter(groups__name='delivery', is_active=True)
            random_delivery = random.choice(delivery).id

            order_data = {
                "user": request.user.id,
                "delivery_crew": random_delivery,
                "status": False,
                "total": total_cart_price,
                "date": timezone.now().date(),
            }

            ser = OrderSerializer(data=order_data)
            if ser.is_valid():
                order = ser.save()

                for item in user_cart:
                    order_item = OrderItem(
                        order=order,
                        menuitem_id=item.menuitem_id,
                        quantity=item.quantity,
                        price=item.price
                    )
                    order_item.save()

                user_cart.delete()

                return Response(ser.data, status=status.HTTP_200_OK)
            else:
                return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
