from django.contrib import admin

from .models import Category, MenuItem, Cart
# Register your models here.
admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Cart)

