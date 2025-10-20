from django import forms
from .models import WasteListing

class WasteListingForm(forms.ModelForm):
    class Meta:
        model = WasteListing
        fields = ['waste_type', 'quantity', 'description', 'location', 'image']
        widgets = {
            'waste_type': forms.Select(attrs={
                'class': 'form-input',
                'placeholder': 'Select waste type'
            }),
            'quantity': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., 5 kg, 10 bags, 1 truckload'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Describe your waste material...',
                'rows': 4
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your location'
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make image field not required
        self.fields['image'].required = False
        # Add custom classes and attributes
        self.fields['description'].widget.attrs.update({
            'maxlength': '100'
        })
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and len(quantity) < 2:
            raise forms.ValidationError("Please provide a valid quantity description.")
        if quantity and len(quantity) > 50:
            raise forms.ValidationError("Quantity description is too long (max 50 characters).")
        return quantity
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description) > 100:
            raise forms.ValidationError("Description is too long (max 100 characters).")
        return description
    
    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location and len(location) < 3:
            raise forms.ValidationError("Please provide a valid location.")
        if location and len(location) > 100:
            raise forms.ValidationError("Location is too long (max 100 characters).")
        return location
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Validate file size (5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large (max 5MB)")
            
            # Validate file type
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            extension = image.name.split('.')[-1].lower()
            if extension not in valid_extensions:
                raise forms.ValidationError(
                    "Unsupported file format. Please upload JPG, PNG, or GIF images."
                )
            
            # Validate file name
            if len(image.name) > 100:
                raise forms.ValidationError("File name is too long.")
        
        return image
