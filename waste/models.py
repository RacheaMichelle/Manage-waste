from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.storage import default_storage
import os

class WasteListing(models.Model):
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    waste_type = models.CharField(max_length=50, choices=WASTE_TYPE_CHOICES)
    quantity = models.CharField(max_length=50, blank=True, help_text="e.g., 2 heaps, 5 sacks, 3 bags")
    description = models.CharField(max_length=100, blank=True, help_text="Additional details about the waste (optional)")
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to='waste_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Waste Listing'
        verbose_name_plural = 'Waste Listings'

    def __str__(self):
        return f"{self.get_waste_type_display()} - {self.user.username}"

    def get_absolute_url(self):
        return reverse('waste_detail', kwargs={'pk': self.pk})

    def get_image_url(self):
        """Safe method to get image URL"""
        if self.image and hasattr(self.image, 'url'):
            try:
                # Check if file exists in storage
                if default_storage.exists(self.image.name):
                    return self.image.url
            except:
                pass
        return None

    def image_exists(self):
        """Check if image file actually exists"""
        if self.image:
            try:
                return default_storage.exists(self.image.name)
            except:
                return False
        return False

    def delete(self, *args, **kwargs):
        """Override delete to remove image file when object is deleted"""
        if self.image:
            # Delete the image file from storage
            if default_storage.exists(self.image.name):
                default_storage.delete(self.image.name)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Override save to handle image cleanup"""
        # If this is an update and image is changed, delete old image
        if self.pk:
            try:
                old_instance = WasteListing.objects.get(pk=self.pk)
                if old_instance.image and old_instance.image != self.image:
                    if default_storage.exists(old_instance.image.name):
                        default_storage.delete(old_instance.image.name)
            except WasteListing.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)

    @property
    def display_quantity(self):
        """Formatted quantity for display"""
        if self.quantity:
            return self.quantity
        return "Not specified"

    @property
    def short_description(self):
        """Shortened description for listings"""
        if self.description and len(self.description) > 50:
            return self.description[:50] + '...'
        return self.description or "No description"

    def get_waste_type_class(self):
        """Return CSS class for waste type badges"""
        return f"waste-type-{self.waste_type}"
