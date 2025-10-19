from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, QuickRegisterForm, ProfileEditForm
from .models import Profile

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('profile')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            # Print form errors for debugging
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = Profile.objects.create(user=request.user)
    
    is_quick_access = profile.user_type == 'quick_access'
    
    return render(request, 'users/profile.html', {
        'profile': profile,
        'is_quick_access': is_quick_access,
    })

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'users/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            
            # Check if next parameter exists
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('profile')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'users/login.html')

# ADD THIS MISSING FUNCTION
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

# ADD THESE MISSING FUNCTIONS TOO
def quick_register(request):
    if request.method == 'POST':
        form = QuickRegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Quick account created!')
                return redirect('quick_dashboard')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = QuickRegisterForm()
    
    return render(request, 'users/quick_register.html', {'form': form})

@login_required
def quick_dashboard(request):
    try:
        profile = request.user.profile
        is_quick_access = profile.user_type == 'quick_access'
    except Profile.DoesNotExist:
        is_quick_access = False
    
    if not is_quick_access:
        return redirect('profile')
    
    return render(request, 'users/quick_dashboard.html', {
        'is_quick_access': is_quick_access,
    })

@login_required
def profile_edit(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileEditForm(instance=profile)
    
    return render(request, 'users/profile_edit.html', {'form': form})
