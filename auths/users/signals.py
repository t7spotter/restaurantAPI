from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile

User = get_user_model()


@receiver(post_save, sender=User)
def make_profile_for_user(sender, instance, created, **kwargs):
    if created:
        if not hasattr(instance, 'profile'):
            user_profile = Profile.objects.create(user=instance)
            user_profile.save()
