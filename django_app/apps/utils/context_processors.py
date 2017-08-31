def get_user_messages(request):
    if request.user.is_authenticated:
        messages = request.user.unread_messages()
        return {'unread_messages': messages}