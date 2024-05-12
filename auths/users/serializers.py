from rest_framework import serializers

from auths.users.models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id',
            'profile',
            'city',
            'country',
            'details',
        ]