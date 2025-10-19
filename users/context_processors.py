from .models import Profile

def quick_access_status(request):
    is_quick_access = False
    if request.user.is_authenticated:
        try:
            if hasattr(request.user, 'profile') and request.user.profile.user_type == 'quick_access':
                is_quick_access = True
        except Profile.DoesNotExist:
            pass
    return {
        'is_quick_access': is_quick_access,
    }
