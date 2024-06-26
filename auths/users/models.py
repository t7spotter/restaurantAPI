from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(_("email address"), blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    ready_to_work = models.BooleanField(_("ready to work"), default=None, null=True, blank=True)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an mail to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=11, blank=True)
    details = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'profiles'
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'

    def __str__(self):
        return f'Profile of {self.user.username}'


class Address(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='addresses')
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    details = models.TextField(blank=False, null=True)

    class Meta:
        db_table = 'Addresses'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'Address of {self.profile.user.username}'
