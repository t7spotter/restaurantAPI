from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from auths.users.models import User


@receiver(post_save, sender=User)
def assign_to_customer_group(sender, instance, created, **kwargs):
    if created:
        if not instance.groups.exists():
            customer_group, _ = Group.objects.get_or_create(name='customer')
            instance.groups.add(customer_group)
