# -*- coding: utf-8 -*-
import json

from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.template.context_processors import static
from django.views.generic import View

from operations.models import UserMessage
from users.models import UserProfile, Group, UserGroup, Organization
from utils.lookup_word_in_db import find_word


class MessageView(View):
    def get(self, request, message_id):
        message = UserMessage.objects.filter(id=message_id).get()
        data = {
            "page": "messages",
            "message": message
        }
        message.has_read = True
        message.save()
        if message.message_type == UserMessage.MSG_TYPE_USER:
            return render(request, 'message_view.html', data)
        else:
            text = message.message
            data.update(json.loads(text))
            if message.message_type == UserMessage.MSG_TYPE_JOIN_GROUP:
                return self.render_msg_join_group(request, data)
            elif message.message_type == UserMessage.MSG_TYPE_LEAVE_GROUP:
                return self.render_msg_leave_group(request, data)
            elif message.message_type == UserMessage.MSG_TYPE_CREATE_GROUP:
                return self.render_msg_create_group(request, data)

    def render_msg_join_group(self, request, data):
        user = UserProfile.objects.filter(id=data["user_id"]).get()
        group = Group.objects.filter(id=data["group_id"]).get()
        if data.get("is_teacher", False):
            data["role"] = 2
        else:
            data["role"] = 1
        data["role_verbose"] = UserGroup(role=data["role"]).get_role_display()
        data.update({
            "user": user,
            "group": group
        })
        return render(request, 'message_join_group.html', data)

    def render_msg_leave_group(self, request, data):
        user = UserProfile.objects.filter(id=data["user_id"]).get()
        group = Group.objects.filter(id=data["group_id"]).get()

        data.update({
            "user": user,
            "group": group
        })
        return render(request, 'message_leave_group.html', data)

    def render_msg_create_group(self, request, data):
        organization_id = data["organization_id"]
        organization = Organization.objects.filter(id=organization_id).get()
        data["organization"] = organization
        return render(request, 'message_create_group.html', data)

    def post(self, request, message_id):
        # this should actually be delete
        UserMessage.objects.filter(id=message_id).delete()
        return redirect(reverse('operations.message_list'))


class MessageListView(View):
    def get(self, request):
        messages = UserMessage.objects.filter(to_user=request.user.id).order_by("-add_time").all()
        return render(request, 'message_list.html', {
            "page": "messages",
            "messages": messages
        })


class DictionaryView(View):
    def get(self, request, spelling):
        # lookup the word
        word = find_word(spelling)
        if not word:
            raise Http404()
        return render(request, "dictionary.html", {
            "word": word
        })


class DictionaryFormView(View):
    def post(self, request):
        spelling = request.POST.get("spelling", "")
        return HttpResponseRedirect(reverse("operations.dictionary", kwargs={"spelling": spelling}))


class HighscoreView(View):
    def get(self, request):
        return render(request, 'todo.html', {
            "page": "highscore"
        })


class AjaxUnreadMessageView(View):
    def get(self, request):
        messages = UserMessage.objects\
            .filter(to_user=request.user.id, has_read=False)\
            .order_by("-add_time").all()
        result = [
            {
                "from_user_nickname": x.from_user.nick_name if x.from_user else u"系统消息",
                "from_user_avatar": x.from_user.avatar.url if x.from_user.avatar else static('AdminLTE/img/avatar2.png'),
                "time": x.add_time.strftime("%Y-%m-%d %H:%M"),
                "title": x.title if x.title else u"无标题",
                "url": reverse("operations.message", kwargs={
                    "message_id": x.id
                })
            }
            for x in messages
        ]
        return JsonResponse({
            "messages": result
        })