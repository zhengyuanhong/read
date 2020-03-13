from django.shortcuts import render, redirect
from .models import siteUser
from index.models import article, comments, notify
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from utils.qiniu import uploadQiniu
from utils.util import get_token, de_token, formateTime, random_str, uploadImg
from celery_task.task import sendMail, sendResetPassUrl
from django.core.cache import cache
import os
import math
import time


def page_not_found(request):
    return render(request, '404.html')


def accountUser(request, userId):
    user = siteUser.objects.get(id=userId)

    return render(request, 'account/account.html', {'user': user})


def accountUserComment(request):
    if request.method == 'GET':
        page = int(request.GET.get('page', 1))
        comm_uid = request.GET.get('userid')
        query = comments.objects.filter(comm_uid=comm_uid)

        data = []
        context = {}
        if page > query.count():
            context['code'] = 200
            context['status'] = 'success'
            context['data'] = data
            return JsonResponse(context)

        limit = 1
        offset_a = (page-1) * limit
        offset_b = page*limit

        userComment = query.all().order_by('-createTime')[offset_a:offset_b]

        for u in userComment:
            temp = {}
            temp['article_id'] = u.aid.id
            temp['article_title'] = u.aid.title
            temp['time'] = formateTime(
                str(u.createTime.strftime("%Y-%m-%d %H:%M:%S")))
            data.append(temp)

        context['code'] = 200
        context['status'] = 'success'
        context['data'] = data
        return JsonResponse(context)


def accountUserArticle(request):
    if request.method == 'GET':
        page = int(request.GET.get('page', 1))
        uid = request.GET.get('userid')

        query = article.objects.filter(uid=uid).filter(is_show=True)

        data = []
        context = {}
        if page > query.count():
            context = {}
            context['code'] = 200
            context['status'] = 'success'
            context['data'] = data
            return JsonResponse(context)

        limit = 1
        offset_a = (page-1) * limit
        offset_b = page*limit

        userArticle = query.all().order_by('-createTime')[offset_a:offset_b]

        for u in userArticle:
            temp = {}
            temp['id'] = u.id
            temp['title'] = u.title
            temp['time'] = formateTime(
                str(u.createTime.strftime("%Y-%m-%d %H:%M:%S")))
            temp['comm_num'] = u.article.count()
            temp['book_name'] = u.category.name
            data.append(temp)

        context['code'] = 200
        context['status'] = 'success'
        context['data'] = data
        return JsonResponse(context)
# 登陆


def accountLogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = siteUser.objects.get(email=email)
        except Exception:
            return JsonResponse({'code': 201, 'msg': '邮箱不存在'})

        res = authenticate(username=user.username, password=password)
        # 查看是否有此用户
        if res is not None:
            if not res.is_verif:
                return JsonResponse({'code': 202, 'msg': '账号未激活'})
            else:
                # 登陆
                login(request, user=res)
                return JsonResponse({'code': 200, 'msg': '登陆成功'})
        else:
            return JsonResponse({'code': 201, 'msg': '用户名或密码错误'})
    return render(request, 'account/login.html')

# 注册


def accountRegister(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')

        if not (len(password) >= 8):
            return JsonResponse({'code': 201, 'msg': '密码长度不够'})
        # 验证两次密码输入是否正确
        if password != repassword:
            return JsonResponse({'code': 201, 'msg': '两次密码的输入不相同'})

        # 邮件唯一
        onlyEmail = siteUser.objects.filter(email=email).first()
        if onlyEmail:
            return JsonResponse({'code': 201, 'msg': '邮箱已被注册'})

        # 用户名唯一
        onlyUsername = siteUser.objects.filter(username=username).first()
        if onlyUsername:
            return JsonResponse({'code': 201, 'msg': '用户名已被使用'})

        # TODO 邮箱验证
        userinfo = {'email': email}
        verif_code = get_token(userinfo)
        # sendVerif(verif_code, email)
        sendMail.delay(verif_code, email)

        siteUser.objects.create_user(
            username=username, email=email, password=password, is_verif=False)

        return JsonResponse({'code': 200, 'msg': '发送邮箱...'})
    return render(request, 'account/reg.html')

# 邮箱发送提醒


def emailTip(request):
    return render(request, 'account/verif.html')

# 邮箱验证过期


def verifEmail(request):
    return render(request, 'account/verif_expire.html')

# 账号激活验证


def verif(request):
    if request.method == 'GET':
        token = request.GET.get('token')
        userinfo = de_token(token)
        if not userinfo:
            return render(request, 'account/verif_expire.html', {'code': 201, 'message': '验证已过期', 'tip': '输入邮箱重新激活'})
        else:
            user = siteUser.objects.filter(email=userinfo['email']).first()
            if user.is_verif:
                return render(request, 'account/verif_suss.html', {'code': 200, 'message': '激活成功', 'tip': '点击这里去登陆'})

            user.is_verif = True
            user.save()

            context = {}
            context['code'] = 200
            context['message'] = '验证成功'
            context['tip'] = '点击这里登陆'
            return render(request, 'account/verif_suss.html', context)

    if request.method == 'POST':
        email = request.POST.get('email')

        res = siteUser.objects.filter(email=email).first()
        if not res:
            return JsonResponse({'code': 201, 'msg': '这不是注册时的邮箱'})
        if res.is_verif:
            return JsonResponse({'code': 203, 'msg': '该邮箱以验证通过'})

        # TODO 邮箱验证
        userinfo = {'email': email}
        verif_code = get_token(userinfo)
        sendVerif(verif_code, email)
        return JsonResponse({'code': 200, 'msg': '发送邮箱...'})

# 登出


def accountLoginOut(request):
    logout(request)
    return HttpResponseRedirect('/')

# 修改密码
@login_required
def setPassword(request):
    if request.method == 'POST':
        oldpassword = request.POST.get('oldpassword')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')

        if not (len(password) >= 8):
            return JsonResponse({'code': 201, 'msg': '密码长度不够'})

        # 判断密码是否重复
        if password != repassword:
            return JsonResponse({'code': 201, 'msg': '两次密码输入不正确'})

        # 判断密码是否正确
        userpass = siteUser.objects.get(id=request.user.id)
        if not check_password(oldpassword, userpass.password):
            return JsonResponse({'code': 201, 'msg': '原密码错误'})
        else:
            siteUser.objects.filter(id=request.user.id).update(
                password=make_password(password))
            return JsonResponse({'code': 200, 'msg': '修改成功'})

# 重置密码


def resetPassword(request):
    if request.method == 'GET':
        token = request.GET.get('token')
        userinfo = de_token(token)
        if not userinfo:
            return render(request, 'account/reset_pass_tip.html', {'message': '验证已过期'})
        else:
            return render(request, 'account/reset_pass_page.html', {'message': token})

    if request.method == 'POST':
        newpassword = request.POST.get('newpassword')
        repassword = request.POST.get('repassword')
        key = request.POST.get('key', None)

        if not key:
            return JsonResponse({'code': 201, 'msg': '非法请求'})

        userinfo = de_token(key)
        if not userinfo:
            return JsonResponse({'code': 201, 'msg': '验证链接已过期，请重新获取'})

        if not (len(newpassword) >= 8):
            return JsonResponse({'code': 201, 'msg': '密码长度不够'})

        # 判断密码是否重复
        if newpassword != repassword:
            return JsonResponse({'code': 201, 'msg': '两次密码输入不正确'})

        user = siteUser.objects.filter(email=userinfo['email'])
        userobj = user.first()
        if not userobj.is_verif:
            return JsonResponse({'code': 201, 'msg': '账号未激活'})

        if not userobj.is_active:
            return JsonResponse({'code': 201, 'msg': '该账号已被禁止登陆'})

        user.update(password=make_password(newpassword))
        return JsonResponse({'code': 200, 'msg': '修改成功'})

# 发送重置密码链接


def sendResetPassword(request):
    if request.method == 'GET':
        return render(request, 'account/reset_pass.html', {'flag': True, 'tip': '请输入正确的邮箱地址（发送邮箱过程可能会有点长，请耐心等待）'})
    if request.method == 'POST':
        email = request.POST.get('email')

        res = siteUser.objects.filter(email=email).first()
        if not res:
            return render(request, 'account/reset_pass.html', {'flag': True, 'tip': '该邮箱未注册'})

        token = get_token({'email': email})
        sendResetPassUrl.delay(token, email, res.username)
        return render(request, 'account/reset_pass.html', {'flag': False, 'tip': '已发送到您的邮箱'})


@login_required
def accountSet(request):
    return render(request, 'account/set.html')

# 修改个人信息


def setInfo(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        qianming = request.POST.get('qianming')
        sex = request.POST.get('sex')

        # 判断邮箱和用户名是否唯一
        query = siteUser.objects.exclude(id=request.user.id)
        exitUser = query.filter(username=username).first()
        if exitUser:
            return JsonResponse({'code': 201, 'msg': '用户名已占用'})
        else:
            user = siteUser.objects.get(id=request.user.id)
            user.username = username
            user.qianming = qianming
            user.sex = sex
            user.save()
            return JsonResponse({'code': 200, 'msg': '修改成功'})

# 上传头像
@csrf_exempt
def uploadImage(request):
    if not siteUser.is_authenticated:
        return JsonResponse({'code': 201, 'msg': '非法请求'})
    if request.method == 'POST':
        status = uploadImg(request, 'avatars')
        if status == 0:
            return JsonResponse({'code': 201, 'msg': '图片太大'})

        if status == 1:
            return JsonResponse({'code': 201, 'msg': '不是我要的格式'})

        if status == 2:
            return JsonResponse({'code': 201, 'msg': '上传失败'})

        try:
            user = siteUser.objects.get(id=request.user.id)
        except Exception:
            return JsonResponse({'code': 201, 'msg': '上传失败'})

        user.avatar = settings.QINIU_DOMAIN + status
        user.save()
        return JsonResponse({'code': 200, 'msg': '上传成功'})


def getMessage(request):
    return render(request, 'account/message.html')

# 获取信息


def getMsg(request):
    if request.method == 'GET':
        message = notify.objects.filter(
            uid=request.user, is_read=0).all().order_by('-createTime')

        data = []
        for m in message:
            temp = {}
            temp['id'] = m.id
            temp['title'] = m.content
            temp['article_id'] = m.aid
            temp['time'] = formateTime(
                str(m.createTime.strftime("%Y-%m-%d %H:%M:%S")))
            data.append(temp)

        context = {}
        context['code'] = 200
        context['status'] = 'success'
        context['data'] = data
        return JsonResponse(context)

# 删除信息


def delMsg(request):
    if request.method == 'GET':
        notify_id = request.GET.get('id', None)

        if notify_id is not None:
            n = notify.objects.filter(id=notify_id, uid=request.user).first()
            n.is_read = 1
            n.save()
        else:
            notify.objects.filter(uid=request.user).update(is_read=1)
        return render(request, 'account/message.html')
