from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import MenuItem
from .serializers import MenuItemSerializer, UserSerializer
from .permissions import IsManager


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
                return Response([{"message": f"{queryset.title} updated"}, ser.data], status=status.HTTP_200_OK)
        else:
            return Response({"message": "You have not permission for this action"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request: Request, pk):
        if request.user.groups.filter(name='manager').exists():  # only manger group members can use delete method
            try:
                queryset = get_object_or_404(MenuItem, pk=pk)
            except MenuItem.DoesNotExist:
                return Response({"message": "This menu item does not exists"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                queryset.delete()
                return Response({"message": f"{queryset.title} Deleted"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "You have not permission for this action"},
                            status=status.HTTP_403_FORBIDDEN)


class ManagerGroupManagement(APIView):
    permission_classes = [IsManager]

    def get(self, request: Request):
        queryset = User.objects.filter(groups__name='manager')
        ser = UserSerializer(queryset, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)

    def post(self, request: Request):
        user = get_object_or_404(User, username=request.data.get('username'))
        managers = get_object_or_404(Group, name='manager')

        user.groups.add(managers)
        return Response({"message": f"{user} added to the manager group"}, status=status.HTTP_201_CREATED)
