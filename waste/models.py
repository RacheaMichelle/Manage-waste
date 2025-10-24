from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from cloudinary.models import CloudinaryField  # CORRECT IMPORT

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
    
    # REPLACE ImageField WITH CloudinaryField
    image = CloudinaryField(
        'image',
        folder='clean_uganda/waste_listings',
        blank=True, 
        null=True,
        transformation=[
            {'width': 800, 'height': 600, 'crop': 'limit'},
            {'quality': 'auto:good'},
        ]
    )
    
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
        """Safe method to get image URL from Cloudinary"""
        if self.image:
            try:
                return self.image.url
            except:
                return None
        return None

    def image_exists(self):
        """Check if image exists in Cloudinary"""
        return bool(self.image)

    # REMOVE the manual file deletion methods - Cloudinary handles this automatically

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