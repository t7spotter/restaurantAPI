from rest_framework import serializers

from .models import Category, MenuItem, Cart, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    model = MenuItem
    fields = ['id', 'slug', 'title']

    class Meta:
        db_table = 'categories'


class MenuItemSerializer(serializers.ModelSerializer):
    model = MenuItem
    fields = ['id', 'title', 'price', 'featured', 'category']

    class Meta:
        db_table = 'menu_items'


class CartSerializer(serializers.ModelSerializer):
    model = Cart
    fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']

    class Meta:
        db_table = 'carts'


class OrderSerializer(serializers.ModelSerializer):
    model = Order
    fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']

    class Meta:
        db_table = 'orders'


class OrderItemSerializer(serializers.ModelSerializer):
    model = OrderItem
    fields = ['id', 'order', 'menuitem', 'quantity', 'price']

    class Meta:
        db_table = 'order_items'
