# from django.contrib.auth.models import User
from django.db import models
from auths.users.models import User


class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    class Meta:
        db_table = 'menu_items'
        verbose_name = 'menu_item'
        verbose_name_plural = 'menu_items'

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    @staticmethod
    def get_total_price(items):
        total_order_price = 0
        for item in items:
            total_order_price += item.price
        return total_order_price

    class Meta:
        # unique_together = ('menuitem', 'user')
        db_table = 'carts'
        verbose_name = 'cart'
        verbose_name_plural = 'carts'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="delivery_crew", null=True)
    status = models.BooleanField(default=0, db_index=True)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    date = models.DateField(db_index=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'order'
        verbose_name_plural = 'orders'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='order')
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('order', 'menuitem')
        db_table = 'order_items'
        verbose_name = 'order_item'
        verbose_name_plural = 'order_items'
