from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile

class UserRegisterForm(UserCreationForm):
    user_type = forms.ChoiceField(
        choices=Profile.USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial='household'
    )
    location = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your location'})
    )
    contact = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+256XXXXXXXXX'})
    )
    accepted_waste_types = forms.MultipleChoiceField(
        choices=Profile.WASTE_TYPE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type', 
                 'location', 'contact', 'accepted_waste_types']

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        if user_type in ['collector', 'recycler']:
            if not cleaned_data.get('contact'):
                self.add_error('contact', "Contact information is required for collectors and recyclers")
            
            if not cleaned_data.get('accepted_waste_types'):
                self.add_error('accepted_waste_types', "Please select at least one waste type")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Get or create profile
            profile, created = Profile.objects.get_or_create(user=user)
            profile.user_type = self.cleaned_data['user_type']
            profile.location = self.cleaned_data['location']
            profile.contact = self.cleaned_data.get('contact', '')
            
            # Convert list to comma-separated string
            waste_types = self.cleaned_data.get('accepted_waste_types', [])
            profile.accepted_waste_types = ','.join(waste_types) if waste_types else ''
            
            profile.save()
        
        return user

class QuickRegisterForm(UserCreationForm):
    user_type = forms.ChoiceField(
        choices=[('quick_access', 'Quick Access')],
        widget=forms.RadioSelect,
        initial='quick_access'
    )
    location = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Optional location'})
    )
    contact = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Optional contact'})
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'user_type', 'location', 'contact']

    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.user_type = self.cleaned_data.get('user_type', 'quick_access')
            profile.location = self.cleaned_data.get('location', '')
            profile.contact = self.cleaned_data.get('contact', '')
            profile.save()
        
        return user

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user_type', 'location', 'contact', 'accepted_waste_types']
        widgets = {
            'user_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'placeholder': 'Enter your location'
            }),
            'contact': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'placeholder': '+256 XXX XXX XXX'
            }),
            'accepted_waste_types': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'placeholder': 'plastic, paper, glass, etc.'
            }),
        }