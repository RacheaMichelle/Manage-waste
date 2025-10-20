from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import WasteListing
from .forms import WasteListingForm

@login_required
def list_waste(request):
    """View to list all waste listings and create new ones"""
    listings = WasteListing.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        form = WasteListingForm(request.POST, request.FILES)
        if form.is_valid():
            waste_listing = form.save(commit=False)
            waste_listing.user = request.user
            waste_listing.save()
            messages.success(request, 'Waste listing created successfully!')
            return redirect('waste_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WasteListingForm()
    
    return render(request, 'waste/list.html', {
        'form': form,
        'listings': listings,
        'active_tab': 'list'
    })

@login_required
def create_waste(request):
    """View specifically for creating waste listings"""
    if request.method == 'POST':
        form = WasteListingForm(request.POST, request.FILES)
        if form.is_valid():
            waste_listing = form.save(commit=False)
            waste_listing.user = request.user
            waste_listing.save()
            messages.success(request, 'Waste listing created successfully!')
            return redirect('waste_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WasteListingForm()
    
    listings = WasteListing.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'waste/list.html', {
        'form': form,
        'listings': listings,
        'active_tab': 'create'
    })

@login_required
def update_waste(request, pk):
    """Update existing waste listing"""
    waste_listing = get_object_or_404(WasteListing, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = WasteListingForm(request.POST, request.FILES, instance=waste_listing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Waste listing updated successfully!')
            return redirect('waste:waste_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WasteListingForm(instance=waste_listing)
    
    listings = WasteListing.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'waste/update.html', {
        'form': form,
        'listings': listings,
        'editing': True,
        'active_tab': 'list'
    })

@login_required
def delete_waste(request, pk):
    """Delete waste listing"""
    waste_listing = get_object_or_404(WasteListing, pk=pk, user=request.user)
    
    if request.method == 'POST':
        waste_listing.delete()
        messages.success(request, 'Waste listing deleted successfully!')
        return redirect('waste_list')
    
    return render(request, 'waste/delete.html', {
        'listing': waste_listing
    })

@login_required
def waste_listings(request):
    """Alternative view for user's waste listings"""
    listings = WasteListing.objects.filter(user=request.user, is_active=True)
    return render(request, 'waste/my_listings.html', {
        'listings': listings
    })

@login_required
def waste_listing_detail(request, pk):
    """View individual waste listing details"""
    listing = get_object_or_404(WasteListing, pk=pk)
    # Check if user owns the listing or it's public
    can_edit = listing.user == request.user
    return render(request, 'waste/listing_detail.html', {
        'listing': listing,
        'can_edit': can_edit
    })

def public_listings(request):
    """Public view of active waste listings"""
    listings = WasteListing.objects.filter(is_active=True).select_related('user')
    unique_users = listings.values('user').distinct().count()
    
    return render(request, 'waste/public_listings.html', {
        'listings': listings,
        'unique_users': unique_users
    })
