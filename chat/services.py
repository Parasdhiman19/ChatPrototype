# chat/services.py
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message
from django.db.models import Q


@database_sync_to_async
def get_message_history(my_id, partner_id):
    messages = Message.objects.filter(
        sender_id__in=[my_id, partner_id],
        receiver_id__in=[my_id, partner_id]
    ).order_by('timestamp')

    return [{
        'sender': msg.sender.username,
        'message': msg.content,
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M')
    } for msg in messages]

@database_sync_to_async
def save_message_to_db(sender_user, partner_id, text):
    partner = User.objects.get(id=partner_id)
    return Message.objects.create(sender=sender_user, receiver=partner, content=text)


@database_sync_to_async
def get_active_chat_users(user):
    interacting_user_ids = Message.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).values_list("sender_id", "receiver_id")

    flat_ids = set()
    for s_id, r_id in interacting_user_ids:
        flat_ids.add(s_id)
        flat_ids.add(r_id)

    flat_ids.discard(user.id)

    users = User.objects.filter(id__in=flat_ids)

    return [
        {
            "id": u.id,
            "username": u.username,
        }
        for u in users
    ]