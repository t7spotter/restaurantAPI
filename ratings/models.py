from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from auths.users.models import User


class Rate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rate = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id'])
        ]
        db_table = 'rates'
        verbose_name = 'rate'
        verbose_name_plural = 'rates'

    def clean(self):
        model_class = self.content_type.model_class()
        try:
            model_instance = model_class.objects.get(pk=self.object_id)
        except model_class.DoesNotExist:
            raise ValidationError('Invalid object_id')
