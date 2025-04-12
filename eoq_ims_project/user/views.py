from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def profile_view(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'user/profile.html', context)