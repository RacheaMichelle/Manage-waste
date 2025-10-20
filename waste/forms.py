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
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and len(quantity) < 2:
            raise forms.ValidationError("Please provide a valid quantity description.")
        return quantity
    
    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location and len(location) < 3:
            raise forms.ValidationError("Please provide a valid location.")
        return location  # Fixed: removed the comma that was creating a tuple
