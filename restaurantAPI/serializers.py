from rest_framework import serializers

from auths.users.models import User
from .models import Category, MenuItem, Cart, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category_title = serializers.CharField(source='category.title', read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id',
                  'title',
                  'category',
                  'category_title',
                  'price',
                  'featured'
                  ]


class CartSerializer(serializers.ModelSerializer):
    menuitem_title = serializers.CharField(source='menuitem.title', read_only=True)
    menuitem_category = serializers.CharField(source='menuitem.category', read_only=True)

    class Meta:
        model = Cart
        fields = ['id',
                  'user',
                  'menuitem',
                  'menuitem_title',
                  'menuitem_category',
                  'quantity',
                  'unit_price',
                  'price'
                  ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'delivered_time']


class OrderItemSerializer(serializers.ModelSerializer):
    menuitem_title = serializers.CharField(source='menuitem.title', read_only=True)
    menuitem_category = serializers.CharField(source='menuitem.category', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id',
                  'order',
                  'menuitem_title',
                  'menuitem_category',
                  'quantity',
                  'price'
                  ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id',
                  'username',
                  'email',
                  'is_staff',
                  'is_active',
                  'is_superuser',
                  'groups',
                  'ready_to_work'
                  ]
