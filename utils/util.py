from django.core.mail import send_mail
from django.conf import settings
from random import Random
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import uuid
import hashlib
import time
import datetime
import os,math
from .qiniu import uploadQiniu

def formateTime(str_time):
    timeArray = time.strptime(str_time, '%Y-%m-%d %H:%M:%S')
    before = int(time.mktime(timeArray))

    time_str = "{} 23:59:59".format(time.strftime('%Y-%m-%d',time.localtime()))
    # 今天最大的时间
    today_last =time.mktime(time.strptime(time_str,'%Y-%m-%d %H:%M:%S'))

    #当前时间
    now = time.time()
    agoTimeTrue = now - before
    agoTime = today_last - before
    agoDay = (math.floor(agoTime/86400))

    if agoTimeTrue < 60:
        return '刚刚'
    elif agoTimeTrue < 3600:
        return '{}分钟前'.format(str(math.ceil(agoTimeTrue/60)))
    elif agoTimeTrue < 3600*12:
        return '{}小时前'.format(str(math.ceil(agoTimeTrue/3600)))
    elif  agoDay == 0:
        return '今天 {}'.format(time.strftime('%H:%M',time.localtime(before)))
    elif  agoDay == 1:
        return '昨天 {}'.format(time.strftime('%H:%M',time.localtime(before)))
    elif  agoDay == 2:
        return '前天 {}'.format(time.strftime('%H:%M',time.localtime(before)))
    elif agoDay > 2 and agoDay < 16:
        return '{num}前天 {time}'.format(num=agoDay,time=time.strftime('%H:%M',time.localtime(before)))
    else:
        flag = True if time.localtime().tm_year != time.localtime(before).tm_year else False 
        if flag:
            return '{}年{}月{}日 {}:{}:{}'.format(timeArray.tm_year, timeArray.tm_mon, timeArray.tm_mday,timeArray.tm_hour,timeArray.tm_min,timeArray.tm_sec)
        else:
            return '{}月{}日 {}:{}:{}'.format(timeArray.tm_mon, timeArray.tm_mday,timeArray.tm_hour,timeArray.tm_min,timeArray.tm_sec)


def get_token(userinfo):
    serializer = Serializer(settings.SECRET_KEY, settings.EXPIRE_TOKEN_TIME)
    userinfo = userinfo
    return serializer.dumps(userinfo).decode()


def de_token(token):
    serializer = Serializer(settings.SECRET_KEY, settings.EXPIRE_TOKEN_TIME)
    try:
        userinfo = serializer.loads(token)
    except Exception:
        return None
    return userinfo


def get_random_str():
    uuid_val = uuid.uuid4()
    uuid_str = str(uuid_val).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(uuid_str)
    return md5.hexdigest()

def random_desc():
    arr = [
        '这万束阳光落下，都照向你，这千百人来回，都与我擦肩。',
        '商人重利轻别离，前月浮梁买茶去。去来江口空守船，绕船明月江水寒。',
        '曾爱惜的总要放手，难接手的又来等候',
        '你是我生命中唯一的阳光，可是这束阳光，却不唯一照耀我。',
        '不想再难过，丢弃回忆重新来过。让涐永远牵着你，把手给我'
    ]
    random = Random()
    index = random.randint(0,len(arr)-1)
    return arr[index]

def sendMail(subject, email_msg, reciever, html_message=None):
    send_mail(
        subject=subject,
        message=email_msg,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=reciever,
        html_message=html_message
    )


def random_str(randomlength=4):
    str = ''
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        i += 1
        str += chars[random.randint(0, length)]
    return str

# 发送重置密码邮箱


def sendResetPassUrl(token, email, username):
    subject = settings.WEB_NAME+'（重置密码）'
    message = ''
    url = '{}/account/reset_password?token={}'.format(settings.HOST_URL, token)
    msg_template = '''
        亲爱的{username}，您收到这封邮件是因为您申请重置密码。
        <br>
        链接有效期：{expires}小时
        <br>
        <a href="{url}" >点击重置密码</a>
        '''
    msg_template = msg_template.format(username=username, expires=int(
        settings.EXPIRE_TOKEN_TIME/3600), url=url)
    sendMail(subject, message, [email], html_message=msg_template)

# 发送验证账号邮箱


def sendVerif(verif_code, email):
    subject = '欢迎注册'+settings.WEB_NAME

    url = '{}/account/verif?token={}'.format(settings.HOST_URL, verif_code)
    message = ''

    msg_template = '''
        有效期：{expires}小时
        <a href="{url}" >点击链接激活</a>
        '''

    html_message = msg_template.format(
        expires=int(settings.EXPIRE_TOKEN_TIME/3600), url=url)
    email_list = [email]
    sendMail(subject, message, email_list, html_message=html_message)


def addJiFen(request, num):
    user = request.user
    user.jifen += num
    user.save()


def reduceJiFen(request, num):
    user = request.user
    if user.jifen < num:
        return False
    else:
        user.jifen -= num
        user.save()
        return True


def getlevel(request):
    jifen = request.user.jifen
    if jifen >= 0 and jifen < 100:
        return 3
    elif jifen >= 100 and jifen < 300:
        return 5
    else:
        return 0


def uploadImg(request, types):
    myfile = request.FILES.get('file')
    if math.ceil(myfile.size/1024) > 200:
        # return JsonResponse({'code': 201, 'msg': '图片太大'})
        return 0

    ext = myfile.name.split('.', 1)[1]
    if ext not in ['jpg', 'png', 'gif']:
        # return JsonResponse({'code': 201, 'msg': '不是我要的格式'})
        return 1

    filepath = os.path.join(settings.MEDIA_ROOT, types, myfile.name)
    f = open(filepath, 'wb')
    for i in myfile.chunks():
        f.write(i)
    f.close()

    # 图片命名
    timename = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    savename = "{}:{}:{}.{}".format(types, request.user.id, timename, ext)

    res = uploadQiniu(filepath, savename)
    if res['key'] != savename:
        # return JsonResponse({'code': 201, 'msg': '上传失败', 'res': res})
        return 2 

    return savename

    # myfile = request.FILES.get('file')
    # if math.ceil(myfile.size/1024) > 200:
    #     return JsonResponse({'code': 201, 'msg': '图片太大'})

    # ext = myfile.name.split('.', 1)[1]
    # if ext not in ['jpg', 'png', 'gif']:
    #     return JsonResponse({'code': 201, 'msg': '不是我要的格式'})

    # filepath = os.path.join(settings.MEDIA_ROOT,'avatars',myfile.name)
    # f = open(filepath, 'wb')
    # for i in myfile.chunks():
    #     f.write(i)
    # f.close()

    # # 图片命名
    # timename = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    # savename = "{}:{}:{}.{}".format(
    #     'userAvatar', request.user.id, timename, ext)

    # res = uploadQiniu(filepath, savename)
    # if res['key'] != savename:
    #     return JsonResponse({'code': 201, 'msg': '上传失败', 'res': res})
    # try:
    #     user = siteUser.objects.get(id=request.user.id)
    # except Exception:
    #     return JsonResponse({'code': 201, 'msg': '上传失败', 'res': res})

    # user.avatar = settings.QINIU_DOMAIN + savename
    # user.save()
    # return JsonResponse({'code': 200, 'msg': '上传成功', 'res': res})