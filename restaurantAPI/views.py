from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import MenuItem
from .serializers import MenuItemSerializer


class ListMenuItems(APIView):
    authentication_classes = [SessionAuthentication]
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
