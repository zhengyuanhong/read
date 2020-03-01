from django.db import models
from django.contrib.auth.models import AbstractUser

class siteUser(AbstractUser):
    sex = models.CharField('性别',max_length=5,choices=(('male','男'),('female','女')),default = 'male')
    level = models.CharField('等级',max_length=4,default='白身')
    jifen = models.IntegerField('积分',default=100)
    qianming = models.CharField('签名',max_length=20,default='这位有点懒')
    avatar = models.URLField('链接',default='http://images.hellozheng.cn/15:2020-01-05-10:38:08.jpg')
    is_verif = models.BooleanField('是否验证',default=False)

    
    class Meta:
        verbose_name_plural = verbose_name='用户'

    def __str__(self):
        return self.username 