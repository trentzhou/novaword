# -*- coding: utf-8 -*-
import json

import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.db.models import Count, Sum
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.templatetags.static import static
from django.views.generic import View

from learn.models import LearningRecord
from operations.models import UserMessage, GroupBook, GroupLearningPlan, UserFeedback
from users.models import UserProfile, Group, UserGroup, Organization
from utils.lookup_word_in_db import find_word


class MessageView(LoginRequiredMixin, View):
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
            elif message.message_type == UserMessage.MSG_TYPE_JOIN_GROUP_OK:
                return self.render_msg_join_group_ok(request, data)


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


    def render_msg_join_group_ok(self, request, data):
        group = Group.objects.filter(id=data["group_id"]).get()
        data.update({"group": group})
        return render(request, "message_join_group_ok.html", data)


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
        user = UserProfile.objects.filter(id=data["user_id"]).get()
        data.update({"user": user})
        return render(request, 'message_create_group.html', data)

    def post(self, request, message_id):
        # this should actually be delete
        UserMessage.objects.filter(id=message_id).delete()
        return redirect(reverse('operations.message_list'))


class MessageListView(LoginRequiredMixin, View):
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
        try:
            detail = json.loads(word.detailed_meanings)
        except:
            detail = {}
        return render(request, "dictionary.html", {
            "word": word,
            "detail": detail
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


class AjaxUnreadMessageView(LoginRequiredMixin, View):
    def get(self, request):
        messages = UserMessage.objects\
            .filter(to_user=request.user.id, has_read=False)\
            .order_by("-add_time").all()
        result = [
            {
                "from_user_nickname": x.from_user.nick_name if x.from_user else u"系统消息",
                "from_user_avatar": x.from_user.avatar.url if x.from_user and x.from_user.avatar else static('AdminLTE/img/avatar2.png'),
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


class AjaxGroupBooksView(LoginRequiredMixin, View):
    def get(self, request, group_id):
        books = GroupBook.objects.filter(group_id=group_id).values("book_id", "book__description")
        return JsonResponse({
            "status": "ok",
            "books": [x for x in books]
        })

    def post(self, request, group_id):
        book_id = request.POST.get("book_id", None)
        # quick hack: I know it's not neat...
        action = request.POST.get('action', "add")
        if not group_id or not book_id:
            return JsonResponse({
                "status": "fail",
                "reason": "bad request"
            })
        if action == "add":
            # create new if not present
            if not GroupBook.objects.filter(group_id=group_id, book_id=book_id).count():
                group_book = GroupBook()
                group_book.group_id = group_id
                group_book.book_id = book_id
                group_book.save()
        elif action == "delete":
            GroupBook.objects.filter(group_id=group_id, book_id=book_id).delete()
        return JsonResponse({
            "status": "ok"
        })


class AjaxGroupLearningPlanView(LoginRequiredMixin, View):
    def get(self, request, group_id):
        units = GroupLearningPlan.objects.filter(group_id=group_id).values("unit_id",
                                                                           "start_date",
                                                                           "unit__book_id",
                                                                           "unit__book__description",
                                                                           "unit__description")
        return JsonResponse({
            "status": "ok",
            "units": [x for x in units]
        })

    def post(self, request, group_id):
        unit_id = request.POST.get("unit_id", None)
        # quick hack: I know it's not neat...
        action = request.POST.get('action', "add")
        start_date = request.POST.get("start_date", None)
        if not start_date:
            start_date = datetime.datetime.today()
        else:
            start_date = datetime.datetime.strptime(start_date, '%Y年%m月%d日')

        if not group_id or not unit_id:
            return JsonResponse({
                "status": "fail",
                "reason": "bad request"
            })
        # create new if not present
        if action == "add":
            existing = GroupLearningPlan.objects.filter(group_id=group_id, unit_id=unit_id)

            if not existing.count():
                group_plan = GroupLearningPlan()
                group_plan.group_id = group_id
                group_plan.unit_id = unit_id
                group_plan.start_date = start_date
                group_plan.save()
            else:
                group_plan = existing.first()
                group_plan.start_date = start_date
                group_plan.save()
        elif action == "delete":
            GroupLearningPlan.objects.filter(group_id=group_id, unit_id=unit_id).delete()
        return JsonResponse({
            "status": "ok"
        })


class UserFeedbackView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_feedback.html', {
            "page": "messages"
        })

    def post(self, request):
        title = request.POST.get("title", "")
        detail = request.POST.get("detail", "")

        msg = UserFeedback()
        msg.reporter = request.user
        msg.title = title
        msg.detail = detail
        msg.save()

        return render(request, 'user_feedback_done.html')


class UserDailySummaryView(LoginRequiredMixin, View):
    def get(self, request, user_id, year, month, day):
        user = UserProfile.objects.filter(id=user_id).get()
        learning_records = LearningRecord.objects.filter(user_id=user_id,
                                                         learn_time__year=year,
                                                         learn_time__month=month,
                                                         learn_time__day=day).all()
        return render(request, 'user_daily_summary.html', {
            "user": user,
            "records": learning_records,
            "date": "{0}-{1}-{2}".format(year, month, day)
        })


class GroupDailySummaryView(LoginRequiredMixin, View):
    def get(self, request, group_id, year, month, day):
        group = Group.objects.filter(id=group_id).get()
        # 看班级里每个人的学习次数
        students = UserProfile.objects.filter(usergroup__group_id=group_id).all()
        learn_records = []
        for s in students:
            records = LearningRecord.objects.filter(user=s,
                                                        learn_time__year=year,
                                                        learn_time__month=month,
                                                        learn_time__day=day).values("user_id").annotate(count=Count("unit"), total_time=Sum("duration"))
            if records:
                record = records[0]
                count = record["count"]
                total_time = record["total_time"]
            else:
                count = 0
                total_time = 0
            learn_records.append({
                "student": s,
                "count": count,
                "total_time": total_time
            })
        return render(request, 'group_daily_summary.html', {
            "group": group,
            "records": learn_records,
            "date": "{0}-{1}-{2}".format(year, month, day),
            "year": year,
            "month": month,
            "day": day
        })


