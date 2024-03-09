from rest_framework import serializers

from .models import Category, MenuItem, Cart, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    model = MenuItem
    fields = ['id', 'slug', 'title']

    class Meta:
        db_table = 'categories'



