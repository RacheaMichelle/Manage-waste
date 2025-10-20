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
            return redirect('waste_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WasteListingForm(instance=waste_listing)
    
    return render(request, 'waste/update.html', {
        'form': form,
        'editing': True,
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
