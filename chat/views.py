from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
from .forms import Message_form
from django.db.models import Q
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import JsonResponse

@login_required
def search_users_api(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'users': []})
        
    matching_users = User.objects.filter(
        username__icontains=query
    ).exclude(id=request.user.id)[:10]
    
    user_data = [
        {'id': user.id, 'username': user.username} 
        for user in matching_users
    ]
    
    return JsonResponse({'users': user_data})

@login_required
def home_view(req):
    interacting_user_ids = Message.objects.filter(
        Q(sender=req.user) | Q(receiver=req.user)
    ).values_list('sender_id', 'receiver_id')
    
    flat_ids = set()
    for s_id, r_id in interacting_user_ids:
        flat_ids.add(s_id)
        flat_ids.add(r_id)
    flat_ids.discard(req.user.id)
    
    active_chat_users = User.objects.filter(id__in=flat_ids)
    return render(
        req,
        "home.html",
        {
            "users": active_chat_users,
        }
    )

@login_required
@xframe_options_exempt
def chat_view(request, user_id):
    chat_partner = User.objects.get(id=user_id)

    return render(
        request,
        "chat_page.html",
        {
            "chat_partner": chat_partner.username,
            "partner_id": chat_partner.id, 
            "my_username": request.user.username,  
        },
    )