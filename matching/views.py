# matching/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from users.models import Profile
from waste.models import WasteListing
from .models import DismissedMatch, Notification
from django.core.paginator import Paginator

@login_required
def matches(request):
    try:
        user_profile = request.user.profile
    except Profile.DoesNotExist:
        messages.error(request, "Please complete your profile first")
        return redirect('profile')

    matches = []
    new_notifications = False

    # Get dismissed listings
    dismissed_ids = DismissedMatch.objects.filter(user=request.user).values_list('listing_id', flat=True)

    if user_profile.user_type in ['household', 'business']:
        listings = WasteListing.objects.filter(user=request.user).exclude(id__in=dismissed_ids).select_related('user')
        
        for listing in listings:
            collectors = Profile.objects.filter(
                user_type__in=['collector', 'recycler'],
                accepted_waste_types__contains=listing.waste_type,
                location=user_profile.location
            ).exclude(contact__isnull=True).exclude(contact__exact='')

            for collector in collectors:
                if not Notification.objects.filter(
                    recipient=request.user,
                    listing=listing,
                    message__contains=collector.user.username
                ).exists():
                    Notification.objects.create(
                        recipient=request.user,
                        listing=listing,
                        message=f"New match! {collector.user.username} ({collector.get_user_type_display()}) can collect your {listing.waste_type} waste."
                    )
                    new_notifications = True

            matches.append({
                'listing': listing,
                'collectors': collectors,
            })

    elif user_profile.user_type in ['collector', 'recycler']:
        accepted_types = user_profile.accepted_waste_types.split(',') if user_profile.accepted_waste_types else []
        listings = WasteListing.objects.filter(
            waste_type__in=accepted_types,
            location=user_profile.location
        ).exclude(user=request.user).exclude(id__in=dismissed_ids)

        for listing in listings:
            listing_owner = Profile.objects.get(user=listing.user)

            if not Notification.objects.filter(
                recipient=request.user,
                listing=listing,
                message__contains=listing.user.username
            ).exists():
                Notification.objects.create(
                    recipient=request.user,
                    listing=listing,
                    message=f"New listing! {listing.user.username} has {listing.quantity}kg of {listing.waste_type} in {listing.location}."
                )
                new_notifications = True

            matches.append({
                'listing': listing,
                'listing_owner': listing_owner,
            })

    if new_notifications:
        messages.info(request, "You have new matches!")

    return render(request, 'matching/matches.html', {
        'matches': matches,
        'user_profile': user_profile
    })

@login_required
def notifications(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at').select_related('listing', 'recipient')
    
    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    unread_notifications = notifications.filter(is_read=False)
    if unread_notifications.exists():
        unread_notifications.update(is_read=True)
        messages.success(request, f"You have {unread_notifications.count()} new notifications")
    
    return render(request, 'matching/notifications.html', {
        'page_obj': page_obj,
        'notifications': page_obj.object_list
    })

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect(request.META.get('HTTP_REFERER', 'notifications'))

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.delete()
    messages.success(request, "Notification deleted successfully.")
    return redirect(request.META.get('HTTP_REFERER', 'notifications'))

@login_required
def clear_all_notifications(request):
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user).delete()
        messages.success(request, "All notifications have been cleared.")
    return redirect('notifications')

@login_required
@require_POST
def delete_match(request, listing_id):
    listing = get_object_or_404(WasteListing, id=listing_id)
    DismissedMatch.objects.get_or_create(user=request.user, listing=listing)
    messages.success(request, "Match deleted successfully.")
    return redirect('matches')

# API endpoints for AJAX polling - PUBLIC (no login required to prevent redirect loops)
@csrf_exempt
def unread_notifications_count(request):
    """
    Public API endpoint for unread notifications count
    Returns 0 for anonymous users to prevent redirect loops
    """
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).count()
        return JsonResponse({'count': count})
    else:
        # Return 0 for anonymous users to prevent redirect loops
        return JsonResponse({'count': 0})

@csrf_exempt
def notifications_api(request):
    """
    Public API endpoint for notifications
    Returns empty array for anonymous users to prevent redirect loops
    """
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:10]
        
        data = {
            'notifications': [
                {
                    'id': n.id,
                    'message': n.message,
                    'is_read': n.is_read,
                    'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
                    'url': f"/matching/notifications/mark-read/{n.id}/" if not n.is_read else ""
                }
                for n in notifications
            ]
        }
        return JsonResponse(data)
    else:
        # Return empty array for anonymous users to prevent redirect loops
        return JsonResponse({'notifications': []})
