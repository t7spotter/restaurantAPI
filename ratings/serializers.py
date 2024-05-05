from rest_framework import serializers

from .models import Rate


class RateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ['id',
                  'user',
                  'rate',
                  'content_type',
                  'object_id'
                  ]
