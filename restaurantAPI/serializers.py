from rest_framework import serializers

from .models import Category, MenuItem, Cart, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    model = Category
    fields = ['id', 'slug', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    model = MenuItem
    fields = ['id', 'title', 'price', 'featured', 'category']


class CartSerializer(serializers.ModelSerializer):
    model = Cart
    fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']


class OrderSerializer(serializers.ModelSerializer):
    model = Order
    fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']


class OrderItemSerializer(serializers.ModelSerializer):
    model = OrderItem
    fields = ['id', 'order', 'menuitem', 'quantity', 'price']
