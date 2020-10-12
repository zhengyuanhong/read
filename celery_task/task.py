from celery_task.celery import app
from readDjango import settings
from django.core.mail import send_mail


import time
@app.task
def test(a,b):
    print(a,b)

@app.task
def regNotfiy(username, email):
    subject = settings.WEB_NAME+'注册通知'
    message = ''

    html_template = '''
      注册名称：{username}；
      <br>
      注册邮箱：{email}；         
      '''

    html_message = html_template.format(username=username, email=email)

    email_list = [settings.EMAIL_HOST_USER]

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=email_list,
        html_message=html_message
    )


@app.task
def sendMail(verif_code, email):
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

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=email_list,
        html_message=html_message
    )


@app.task
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

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        html_message=msg_template
    )
