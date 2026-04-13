from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import UserManager

import uuid


class User(AbstractBaseUser, PermissionsMixin):
    uid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_("Unique identifier for the user")
    )
    username = models.CharField(
        max_length=150,
        verbose_name=_("Username"),
        unique=True
    )
    email = models.EmailField(
        help_text=_("Email address"),
        unique=True
    )

    # ---------------------------- Extra Fields ---------------------------------
    first_name = models.CharField(_("First Name"), max_length=150, null=True, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=150, null=True, blank=True)
    # ---------------------------------------------------------------------------
    
    # Status flags
    is_active = models.BooleanField(
        default=True,
        help_text=_("Designates whether this user should be treated as active")
    )
    is_staff = models.BooleanField(
        default=False,
        help_text=_("Designates whether the user can log into this admin site")
    )
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['username', 'is_active']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def get_full_name(self):
        return self.username
    
    def get_short_name(self):
        return self.username

