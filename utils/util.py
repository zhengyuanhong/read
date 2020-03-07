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
    now = time.time()

    newTime = now - before

    if newTime < 60 and newTime >= 0:
        return '{}秒前'.format(str(round(newTime)))
    elif newTime >= 60 and newTime < 3600:
        return '{}分钟前'.format(str(round(newTime/60)))
    elif newTime >= 3600 and newTime < 86400:
        return '{}小时前'.format(str(round(newTime/3600)))
    elif newTime >= 86400 and newTime < 604800:
        return '{}天前'.format(str(round(newTime/86400)))
    else:
        return '{}年{}月{}日'.format(timeArray.tm_year, timeArray.tm_mon, timeArray.tm_mday)


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