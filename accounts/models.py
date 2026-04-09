from django.conf import settings
from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL)
    phone_number = models.CharField(max_length=25, blank=True)
    company = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    marketing_opt_in = models.BooleanField(default=False)
    interests = models.CharField(
        max_length=255,
        blank=True,
        help_text='Marketing tags, product interests, or audience segments',
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f'{self.user.username} Profile'


class GuestBuyer(models.Model):
    first_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80, blank=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=25, blank=True)
    source = models.CharField(max_length=120, blank=True, help_text='Referral source or acquisition channel')
    marketing_opt_in = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Guest Buyer'
        verbose_name_plural = 'Guest Buyers'
        ordering = ['-created_at']

    def __str__(self):
        return self.email
