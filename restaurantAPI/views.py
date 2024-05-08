import datetime
import random
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.db.models import Sum, Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from auths.users.models import User
from ratings.models import Rate
from ratings.serializers import RateCreateSerializer
from .models import MenuItem, Cart, OrderItem, Order, Category
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer, CategorySerializer, \
    OrderItemSerializer, MenuItemAvailabilitySerializer
from .permissions import IsManager, IsDeliveryCrew, IsCustomer, IsCustomerAndHasBoughtItem, IsManagerOrCustomerReadOnly, \
    IsCustomerOrManagerReadOnly


class ListCategory(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsManagerOrCustomerReadOnly]

    def get(self, request: Request, pk=None):
        if pk:
            queryset = get_object_or_404(Category, pk=pk)
            ser = CategorySerializer(queryset)
            return Response(ser.data, status=status.HTTP_200_OK)
        elif not pk:
            queryset = Category.objects.all()
            ser = CategorySerializer(queryset, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)

    def post(self, request: Request, pk=None):
        if pk:
            return Response({"message": "The post method has not to get pk argument"},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            ser = CategorySerializer(data=request.data)
            if ser.is_valid():
                ser.save()
                return Response(ser.data, status.HTTP_201_CREATED)
            else:
                return Response(ser.errors, status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request, pk):
        try:
            queryset = get_object_or_404(Category, pk=pk)
            ser = CategorySerializer(queryset, data=request.data)
        except Category.DoesNotExist:
            return Response({"message": "This menu item does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        if ser.is_valid():
            ser.save()
            return Response([{"message": f"'{queryset.title}' updated"}, ser.data], status=status.HTTP_200_OK)

    def delete(self, request: Request, pk):
        try:
            queryset = get_object_or_404(Category, pk=pk)
        except Category.DoesNotExist:
            return Response({"message": "This menu item does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            queryset.delete()
            return Response({"message": f"'{queryset.title}' Deleted"}, status=status.HTTP_204_NO_CONTENT)


class ListMenuItems(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsManagerOrCustomerReadOnly]

    def get_queryset(self, pk=None):
        if pk:
            queryset = get_object_or_404(MenuItem, pk=pk)
        else:
            queryset = MenuItem.objects.all().select_related('category')

        search = self.request.query_params.get('search', None)
        categories = self.request.query_params.getlist('category', [])
        to_price = self.request.query_params.get('to_price', None)
        from_price = self.request.query_params.get('from_price', None)
        featured_items = self.request.query_params.get('featured', None)

        if search:
            queryset = queryset.filter(title__icontains=search)

        if categories:
            category_query = Q()
            for category in categories:
                category_query = category_query | Q(category__title__icontains=category)
            queryset = queryset.filter(category_query)

        if to_price:
            queryset = queryset.filter(price__lte=float(to_price))

        if from_price:
            queryset = queryset.filter(price__gte=float(from_price))

        if featured_items:
            queryset = queryset.filter(featured=True)

        return queryset

    def get(self, request: Request, pk=None):
        if pk:
            queryset = self.get_queryset(pk=pk)
            ser = MenuItemSerializer(queryset)
            return Response(ser.data, status=status.HTTP_200_OK)
        else:
            queryset = self.get_queryset().order_by('category', '-featured')
            ser = MenuItemSerializer(queryset, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)

    def post(self, request: Request, pk=None):
        if pk:
            return Response({"message": "The post method has not to get pk argument"},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            ser = MenuItemSerializer(data=request.data)
            if ser.is_valid():
                ser.save()
                return Response(ser.data, status.HTTP_201_CREATED)
            else:
                return Response(ser.errors, status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request, pk):
        try:
            queryset = self.get_queryset(pk=pk)
            ser = MenuItemSerializer(queryset, data=request.data)
        except MenuItem.DoesNotExist:
            return Response({"message": "This menu item does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        if ser.is_valid():
            ser.save()
            return Response([{"message": f"'{queryset.title}' updated"}, ser.data], status=status.HTTP_200_OK)

    def delete(self, request: Request, pk):
        try:
            queryset = get_object_or_404(MenuItem, pk=pk)
        except MenuItem.DoesNotExist:
            return Response({"message": "This menu item does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            queryset.delete()
            return Response({"message": f"'{queryset.title}' Deleted"}, status=status.HTTP_204_NO_CONTENT)


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

        user.is_staff = True  # manager group users must be staff
        user.save()

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

    def get(self, request: Request, pk=None):
        if request.user.groups.filter(name='manager').exists():
            if pk:
                queryset = Cart.objects.filter(user__id=pk)
                user_total_cart_info = queryset.aggregate(
                    total_price=Sum("price"),
                    number_of_items=Count("id"),
                    total_quantity=Sum("quantity")
                )
                ser = CartSerializer(queryset, many=True)
                return Response([ser.data, user_total_cart_info], status=status.HTTP_200_OK)
            elif not pk:
                queryset = Cart.objects.order_by('user').all()
                each_user_cart = queryset.values('user').annotate(total_price=Sum('price'))
                ser = CartSerializer(queryset, many=True)
                return Response([ser.data, each_user_cart], status=status.HTTP_200_OK)

        elif request.user.groups.filter(name='customer').exists():
            queryset = Cart.objects.filter(user=request.user)
            ser = CartSerializer(queryset, many=True)

            total_items = queryset.aggregate(
                total_price=Sum("price"),
                number_of_items=Count("id"),
                total_quantity=Sum("quantity")
            )

            return Response([{"items in your cart": ser.data}, {"total order": total_items}],
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
            if menu_item.featured:

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
            elif not menu_item.featured:
                return Response({"error": "Sorry, this menu item is no longer available."}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User is not in the "customer" group.'}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request: Request):  # TODO: Add pk parameter
        if request.user.groups.filter(name="customer"):
            queryset = Cart.objects.filter(user=request.user)
            queryset.delete()
            return Response({"messages": "Cart cleared"}, status=status.HTTP_204_NO_CONTENT)

    # def get_total_price(self, items):
    #     total_order_price = 0
    #     for item in items:
    #         total_order_price += item.price
    #     return total_order_price


class OrderManagement(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsCustomerOrManagerReadOnly]

    def get(self, request: Request, pk=None):
        if request.user.groups.filter(name='manager'):
            if pk:
                queryset = get_object_or_404(Order, pk=pk)
                ser = OrderSerializer(queryset)
                return Response(ser.data, status=status.HTTP_200_OK)
            elif not pk:
                queryset = Order.objects.order_by('-date', 'user').all()
                ser = OrderSerializer(queryset, many=True)
                return Response(ser.data, status=status.HTTP_200_OK)

        elif request.user.groups.filter(name='customer'):
            if pk:
                queryset = get_object_or_404(Order, pk=pk, user=request.user)
                ser = OrderSerializer(queryset)
                return Response(ser.data, status=status.HTTP_200_OK)
            elif not pk:
                queryset = Order.objects.filter(user=request.user).order_by('date')
                ser = OrderSerializer(queryset, many=True)
                return Response(ser.data, status=status.HTTP_200_OK)

    def post(self, request: Request):
        cart_items = Cart.objects.filter(user=request.user).count()
        if cart_items == 0:
            return Response({"messages": "No items in your cart"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user_cart = Cart.objects.filter(user=request.user)
            total_cart_price = user_cart.aggregate(total_price=Sum("price"))['total_price']
            delivery = User.objects.filter(groups__name='delivery', is_active=True, ready_to_work=True)
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


class OrderDeliveryStatusManagement(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsDeliveryCrew]

    def get(self, request: Request, pk=None):
        if pk:
            order = get_object_or_404(Order, delivery_crew__username=request.user.username, pk=pk)
            ser = OrderSerializer(order)
            return Response(ser.data, status=status.HTTP_200_OK)
        elif not pk:
            orders = Order.objects.filter(delivery_crew__username=request.user.username)
            ser = OrderSerializer(orders, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)

    def post(self, request: Request, pk):
        if request.user.groups.filter(name='delivery'):
            if pk:
                order = get_object_or_404(Order, delivery_crew__username=request.user.username, pk=pk)

                if order.delivered_time is None and order.status is False:
                    order.status = True
                    now_time = str(datetime.datetime.now())[:-7]
                    order.delivered_time = now_time
                    order.save()
                else:
                    return Response({"message": f"Order number {order.id} has already been delivered"})

                ser = OrderSerializer(order)
                return Response({"order": ser.data, "message": f"Order number {order.id} delivered successfully"},
                                status=status.HTTP_200_OK)


class DeliveryCrewReadyToWorkStatusManagement(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsDeliveryCrew]

    def post(self, request: Request):
        queryset = get_object_or_404(User, username=request.user.username)
        if queryset.ready_to_work is True:
            queryset.ready_to_work = False

        elif queryset.ready_to_work is False:
            queryset.ready_to_work = True

        elif queryset.ready_to_work is None:
            queryset.ready_to_work = False

        queryset.save()
        ser = UserSerializer(queryset)
        return Response({"ready_to_work": ser.data["ready_to_work"]}, status=status.HTTP_200_OK)


class OrderDeliveryCrewChanger(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsManager]

    def get(self, request: Request, pk=None):
        if pk:
            queryset = get_object_or_404(Order, status=False, pk=pk)
            ser = OrderSerializer(queryset)
            return Response(ser.data, status=status.HTTP_200_OK)
        elif not pk:
            queryset = Order.objects.filter(status=False).order_by('date')
            ser = OrderSerializer(queryset, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)

    def post(self, request: Request, pk):
        if not pk:
            return Response({"message": "You should specify the pk"}, status=status.HTTP_400_BAD_REQUEST)
        elif pk:
            try:
                delivery_crew_id = request.data['delivery_crew']
            except KeyError:
                return Response({"error": "Please sent a valid delivery crew ID"}, status=status.HTTP_400_BAD_REQUEST)

            alternative_delivery_crew = get_object_or_404(User, groups__name='delivery', pk=delivery_crew_id)

            if alternative_delivery_crew.ready_to_work:
                order = get_object_or_404(Order, pk=pk)
                order.delivery_crew = alternative_delivery_crew
                order.save()
                ser = OrderSerializer(order)
                return Response([{"message": f"Order {order.id} assigned to {alternative_delivery_crew.username}"},
                                 {"order": ser.data}], status=status.HTTP_200_OK)

            elif not alternative_delivery_crew.ready_to_work:
                return Response({'error': 'This delivery crew is not ready to work, please choose another crew.'},
                                status=status.HTTP_404_NOT_FOUND)


class DeliveredOrders(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsManager]

    def get(self, request: Request, pk=None):
        if pk:
            queryset = get_object_or_404(Order, status=True, pk=pk)
            ser = OrderSerializer(queryset)
            return Response(ser.data, status=status.HTTP_200_OK)
        else:
            queryset = Order.objects.filter(status=True).order_by('date')
            ser = OrderSerializer(queryset, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)


class MenuItemAvailability(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsManager]

    def get(self, request: Request, pk=None):
        if pk:
            menuitem = get_object_or_404(MenuItem, pk=pk)
            return Response(
                {"message": f"{menuitem.title} {menuitem.category.title} availability status is: {menuitem.featured}"},
                status=status.HTTP_200_OK)
        elif not pk:
            featured = request.query_params.get('featured')

            if featured:
                if featured in ("True", "true"):
                    queryset = MenuItem.objects.filter(featured=True).order_by('category')
                    queryset_name = "Available Items"
                elif featured in ("False", "false"):
                    queryset = MenuItem.objects.filter(featured=False).order_by('category')
                    queryset_name = "not-available Items"
                else:
                    queryset = MenuItem.objects.filter(featured=True).order_by('category')
                    queryset_name = "Available Items"

                ser = MenuItemAvailabilitySerializer(queryset, many=True)
                return Response([queryset_name, ser.data], status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'please use menuitem id in url or post menuitem name in this format: {"menuitem": "menuitem title"} or use ?featured=true (or false) in url'},
                    status=status.HTTP_400_BAD_REQUEST)

    def post(self, request: Request, pk=None):
        if pk:
            menuitem = get_object_or_404(MenuItem, pk=pk)
        elif 'menuitem' in request.data:
            target_menuitem = request.data['menuitem']
            menuitem = get_object_or_404(MenuItem, title__icontains=target_menuitem)
        else:
            return Response({"error": "Missing 'menuitem' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        if menuitem.featured:
            menuitem.featured = False
        elif not menuitem.featured:
            menuitem.featured = True
        menuitem.save()

        if request.path_info == f"/api/menuitemstatus/{menuitem.id}":
            return_value = Response(
                {"message": f"{menuitem.title} {menuitem.category.title} availability changed to: {menuitem.featured}"},
                status=status.HTTP_200_OK)
        else:
            return_value = redirect(f"/api/menuitemstatus/{menuitem.id}")

        return return_value


class UserOrdersHistory(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsCustomer]

    def get(self, request: Request, pk=None):
        if pk:
            order_items = OrderItem.objects.filter(order=pk).order_by('-price')
            order_items_total_price = order_items.aggregate(total_price=Sum("price"))
            print(UserOrdersHistory)
            ser = OrderItemSerializer(order_items, many=True)
            return Response([ser.data, order_items_total_price], status=status.HTTP_200_OK)
        elif not pk:
            orders = Order.objects.filter(user=request.user).order_by('date')
            ser = OrderSerializer(orders, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)


class MenuItemPriceAdjustment(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsManager]

    def get(self, request: Request, pk=None):
        if pk:
            menuitem = get_object_or_404(MenuItem, pk=pk)
            return Response({"message": f"The {menuitem.title} {menuitem.category.title} price is {menuitem.price}."},
                            status=status.HTTP_200_OK)
        elif not pk:
            return Response({
                'message': 'please use menuitem id in url or post menuitem name in this format: {"menuitem": "menuitem title"}'},
                status=status.HTTP_400_BAD_REQUEST)

    def post(self, request: Request, pk=None):
        if pk:
            menuitem = get_object_or_404(MenuItem, pk=pk)
        elif 'menuitem' in request.data:
            target_menuitem = request.data.get('menuitem')
            menuitem = get_object_or_404(MenuItem, title__icontains=target_menuitem)
        else:
            return Response({"error": "Missing 'menuitem' or 'pk' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_price = request.data.get('price')
        except IntegrityError:
            return Response({"error": "Missing 'price' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        menuitem.price = new_price
        menuitem.save()

        if request.path_info == f"/api/price-change/{menuitem.id}":
            return_value = Response(
                {"message": f"{menuitem.title} {menuitem.category.title} price changed to: {menuitem.price}"},
                status=status.HTTP_200_OK)
        else:
            return_value = redirect(f"/api/price-change/{menuitem.id}")

        return return_value


class SaleReport(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsManager]

    def get(self, request: Request):
        today = timezone.now()
        today_str = str(today)[:-13]

        sales = Order.objects.filter(date=today)

        sales_price = sales.aggregate(total_sale=Sum('total'))['total_sale']
        sales_count = sales.count()

        return Response({"message": f"Today ({today_str}) sale is {sales_price} for {sales_count} orders."},
                        status=status.HTTP_200_OK)

    def post(self, request: Request):
        today = str(timezone.now())[:-22]

        start_date = request.data.get('start_date', today)
        end_date = request.data.get('end_date', today)

        sales = Order.objects.filter(date__range=[start_date, end_date])

        sales_price = sales.aggregate(total_sale=Sum('total'))['total_sale']
        sales_count = sales.count()

        if start_date == end_date:
            return_value, _status = {
                "message": f"Your sale from {start_date} to {end_date} (just today) is {sales_price} for {sales_count} orders."}, status.HTTP_200_OK
        elif start_date < end_date:
            return_value, _status = {
                "message": f"Your sale from {start_date} to {end_date} is {sales_price} for {sales_count} orders."}, status.HTTP_200_OK
        else:
            return_value, _status = {
                "error": "Your start_date must be earlier than the end_date"}, status.HTTP_400_BAD_REQUEST

        return Response(return_value, status=_status)


class MenuItemRatings(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsCustomerAndHasBoughtItem]

    def get(self, request: Request, pk=None):
        if pk:
            queryset = get_object_or_404(MenuItem, pk=pk)
            ser = MenuItemSerializer(queryset)
            return Response(ser.data, status=status.HTTP_200_OK)
        else:
            queryset = MenuItem.objects.all()
            ser = MenuItemSerializer(queryset, many=True)
            return Response(ser.data, status=status.HTTP_200_OK)

    def post(self, request: Request, pk):
        user_past_rate_for_this_item = Rate.objects.filter(user_id=request.user.id, object_id=pk).exists()
        if user_past_rate_for_this_item:
            return Response({"error": "You had rate for this item before."}, status=status.HTTP_403_FORBIDDEN)
        else:
            try:
                user_rate = request.data['rate']
                menuitem = get_object_or_404(MenuItem, pk=pk).id
            except (ValueError, KeyError):
                return Response(
                    {
                        "error": "'rate' field is required. 'rate' must be an integer between 1 to 10."},
                    status=status.HTTP_400_BAD_REQUEST)

        content_type = ContentType.objects.get(app_label='restaurantAPI', model='menuitem').id

        rate_data = {
            "user": request.user.id,
            "rate": user_rate,
            "content_type": content_type,
            "object_id": menuitem,
        }
        ser = RateCreateSerializer(data=rate_data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status.HTTP_201_CREATED)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
