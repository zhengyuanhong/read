from django.shortcuts import render, redirect
from .models import siteUser
from index.models import article,comments,notify
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from utils.qiniu import uploadQiniu
from utils.util import get_token, de_token, sendVerif,formateTime,random_str,sendResetPassUrl
from django.core.cache import cache
import os,math,time

def page_not_found(request):
    return render(request,'404.html')
    
def accountUser(request, userId):
    user = siteUser.objects.get(id=userId)
    return render(request, 'account/account.html', {'user': user})

def accountUserComment(request):
    if request.method == 'GET':
        userComment = comments.objects.filter(comm_uid=request.GET.get('userid')).all().order_by('-createTime')

        data=[]
        for u in userComment:
            temp={}
            temp['article_id'] = u.aid.id
            temp['article_title']=u.aid.title
            temp['time'] = formateTime(str(u.createTime.strftime("%Y-%m-%d %H:%M:%S")))
            data.append(temp)

        context = {}
        context['code'] = 200
        context['status'] = 'success'
        context['data'] = data
        return JsonResponse(context)



def accountUserArticle(request):
    if request.method == 'GET':
        userArticle = article.objects.filter(uid=request.GET.get('userid')).filter(is_show=True).all().order_by('-createTime')

        data=[]    
        for u in userArticle:
            temp = {}
            temp['id']=u.id
            temp['title']=u.title
            temp['time']= formateTime(str(u.createTime.strftime("%Y-%m-%d %H:%M:%S")))
            temp['comm_num']=u.article.count()
            data.append(temp)

        context = {}
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
                # return render(request,'account/login.html',{'message':'邮箱不存在'})
                return JsonResponse({'code': 201, 'msg': '邮箱不存在'})

            res = authenticate(username=user.username, password=password)
            # 查看是否有此用户
            if res is not None:
                if not res.is_verif:
                    # return render(request,'account/login.html',{'message':'账号未激活','flag':True})
                    return JsonResponse({'code': 202, 'msg': '账号未激活'})      
                else:
                    # 登陆
                    login(request, user=res)
                    return JsonResponse({'code': 200, 'msg': '登陆成功'})   
            else:
                # return render(request,'account/login.html',{'message':'用户名或密码错误'})
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
        res = sendVerif(verif_code, email)
        if not res:
            return JsonResponse({'code': 201, 'msg': '检查邮箱是否正确'})

        siteUser.objects.create_user(
            username=username, email=email, password=password, is_verif=False)
        return JsonResponse({'code': 200, 'msg': '发送邮箱...'})
    return render(request, 'account/reg.html')

# 邮箱发送提醒
def emailTip(request):
    return render(request,'account/verif.html')

# 邮箱验证过期
def verifEmail(request):
    return render(request,'account/verif_expire.html')

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
        userinfo = de_token(request.GET.get('token'))
        if not userinfo:
            return render(request, 'account/reset_pass_sucess.html', {'message': '验证已过期'})
        else:
            new_pass = random_str(10)
            siteUser.objects.filter(email=userinfo['email']).update(password=make_password(new_pass))
            res = '您重置的新密码：'+  new_pass
            return render(request,'account/reset_pass_sucess.html',{'message':'密码重置成功','res':res}) 

# 发送重置密码链接
def sendResetPassword(request):
    if request.method == 'GET':
        return render(request,'account/reset_pass.html',{'flag':True,'tip':'请输入正确的邮箱地址'})
    if request.method == 'POST':
        email = request.POST.get('email')

        res = siteUser.objects.filter(email=email).first()
        if not res:
            return render(request,'account/reset_pass.html',{'flag':True,'tip':'该邮箱未注册'})

        token = get_token({'email':email}) 
        sendResetPassUrl(token,email,res.username)
        return render(request,'account/reset_pass.html',{'flag':False,'tip':'已发送到您的邮箱'})


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
        myfile = request.FILES.get('file')
        if math.ceil(myfile.size/1024) > 200:
            return JsonResponse({'code': 201, 'msg': '图片太大'})

        ext = myfile.name.split('.', 1)[1]
        if ext not in ['jpg', 'png', 'gif']:
            return JsonResponse({'code': 201, 'msg': '不是我要的格式'})

        filepath = os.path.join(settings.MEDIA_ROOT,'media/avatar', myfile.name)
        f = open(filepath, 'wb')
        for i in myfile.chunks():
            f.write(i)
        f.close()
        # 图片命名
        timename = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
        savename = "{}:{}:{}.{}".format(
            'userAvatar', request.user.id, timename, ext)

        res = uploadQiniu(filepath, savename)
        if res['key'] != savename:
            return JsonResponse({'code': 201, 'msg': '上传失败', 'res': res})
        try:
            user = siteUser.objects.get(id=request.user.id)
        except Exception:
            return JsonResponse({'code': 201, 'msg': '上传失败', 'res': res})

        user.avatar = settings.QINIU_DOMAIN + savename
        user.save()
        return JsonResponse({'code': 200, 'msg': '上传成功', 'res': res})


def getMessage(request):
    return render(request,'account/message.html')

# 获取信息
def getMsg(request):
    if request.method == 'GET':
        message = notify.objects.filter(uid=request.user,is_read=0).all().order_by('-createTime')

        data=[]
        for m in message:
            temp={}
            temp['id'] = m.id
            temp['title'] = m.content
            temp['article_id'] = m.aid
            temp['time'] = formateTime(str(m.createTime.strftime("%Y-%m-%d %H:%M:%S")))
            data.append(temp)

        context = {}
        context['code'] = 200
        context['status'] = 'success'
        context['data'] = data
        return JsonResponse(context)

# 删除信息
def delMsg(request):
    if request.method == 'GET':
        notify_id = request.GET.get('id',None)

        if notify_id is not None:
            n = notify.objects.filter(id=notify_id,uid=request.user).first()
            n.is_read = 1
            n.save()
        else:
            notify.objects.filter(uid=request.user).update(is_read=1)
        return render(request,'account/message.html') 