from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    USER_TYPE_CHOICES = [
        ('household', 'Household'),
        ('business', 'Business'),
        ('collector', 'Collector'),
        ('recycler', 'Recycler'),
        ('quick_access', 'Quick Access'),
    ]

    WASTE_TYPE_CHOICES = [
        ('plastic', 'Plastic'),
        ('paper', 'Paper'),
        ('glass', 'Glass'),
        ('organic', 'Organic'),
        ('metal', 'Metal'),
        ('e-waste', 'E-Waste'),
        ('clothing', 'Clothing'),
        ('hazardous', 'Hazardous'),
        ('construction', 'Construction'),
        ('medical', 'Medical'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES, 
        default='household'
    )
    location = models.CharField(max_length=100, blank=True)
    contact = models.CharField(
        max_length=15, 
        blank=True,
        help_text="Phone number in format: +256XXXXXXXXX"
    )
    accepted_waste_types = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Comma-separated list of accepted waste types"
    )

    def clean(self):
        """Custom validation"""
        if self.user_type in ['collector', 'recycler']:
            if not self.contact:
                raise ValidationError({"contact": "Contact information is required for collectors/recyclers"})
            if not self.accepted_waste_types:
                raise ValidationError({"accepted_waste_types": "At least one waste type must be selected for collectors/recyclers"})

    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_user_type_display(self):
        """Get display value for user_type"""
        for choice in self.USER_TYPE_CHOICES:
            if choice[0] == self.user_type:
                return choice[1]
        return "Unknown"

    def get_accepted_waste_types_list(self):
        """Convert comma-separated waste types to list"""
        if self.accepted_waste_types:
            return [waste.strip() for waste in self.accepted_waste_types.split(',')]
        return []

    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"

# Signal to automatically create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.get_or_create(user=instance)