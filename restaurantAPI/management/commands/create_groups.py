from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):   # Should name it "Command"
    help = 'Create default groups'

    def handle(self, *args, **options):
        groups = ['delivery', 'manager', 'customer']
        for group_name in groups:
            Group.objects.get_or_create(name=group_name)
        self.stdout.write(self.style.SUCCESS('Groups created successfully'))