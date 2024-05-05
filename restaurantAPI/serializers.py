from django.db.models import Avg, Count
from rest_framework import serializers

from auths.users.models import User
from .models import Category, MenuItem, Cart, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    _category_title = serializers.CharField(source='category.title', read_only=True)
    rate = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ['id',
                  'title',
                  'category',
                  '_category_title',
                  'price',
                  'featured',
                  'rate'
                  ]

    def get_rate(self, obj):
        rate = obj.rate.aggregate(rate_count=Count('rate'), rate_average=Avg('rate'))
        if rate:
            return rate
        else:
            return 0


class CartSerializer(serializers.ModelSerializer):
    _menuitem_title = serializers.CharField(source='menuitem.title', read_only=True)
    _menuitem_category = serializers.CharField(source='menuitem.category', read_only=True)

    class Meta:
        model = Cart
        fields = ['id',
                  'user',
                  'menuitem',
                  '_menuitem_title',
                  '_menuitem_category',
                  'quantity',
                  'unit_price',
                  'price'
                  ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'delivered_time']


class OrderItemSerializer(serializers.ModelSerializer):
    _menuitem_title = serializers.CharField(source='menuitem.title', read_only=True)
    _menuitem_category = serializers.CharField(source='menuitem.category', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id',
                  'order',
                  '_menuitem_title',
                  '_menuitem_category',
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


class MenuItemAvailabilitySerializer(serializers.ModelSerializer):
    _category_title = serializers.CharField(source='category.title', read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id',
                  'title',
                  '_category_title',
                  ]
