from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import WasteListing
from .forms import WasteListingForm

@login_required
def create_waste_listing(request):
    if request.method == 'POST':
        form = WasteListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            messages.success(request, 'Waste listing created successfully!')
            return redirect('waste_listings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WasteListingForm()
    
    # Get user's active listings
    listings = WasteListing.objects.filter(user=request.user, is_active=True)
    
    return render(request, 'waste/list.html', {
        'form': form,
        'listings': listings
    })

@login_required
def update_waste_listing(request, pk):
    listing = get_object_or_404(WasteListing, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = WasteListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Waste listing updated successfully!')
            return redirect('waste_listings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WasteListingForm(instance=listing)
    
    return render(request, 'waste/update.html', {
        'form': form,
        'listing': listing
    })

@login_required
def delete_waste_listing(request, pk):
    listing = get_object_or_404(WasteListing, pk=pk, user=request.user)
    
    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Waste listing deleted successfully!')
        return redirect('waste_listings')
    
    return render(request, 'waste/delete.html', {
        'listing': listing
    })

@login_required
def waste_listings(request):
    listings = WasteListing.objects.filter(user=request.user, is_active=True)
    return render(request, 'waste/my_listings.html', {
        'listings': listings
    })

@login_required
def waste_listing_detail(request, pk):
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
    return render(request, 'waste/public_listings.html', {
        'listings': listings
    })
