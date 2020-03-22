from django.db import models
from django.conf import settings


class article(models.Model):
    select_type = (
        (1,'公告'),
        (2,'通知'),
        (3,'讨论'),
    )

    title = models.CharField('标题', max_length=50)
    content = models.TextField('内容')
    category = models.ForeignKey('category',on_delete=models.SET_NULL,null=True,blank=True,verbose_name='分类')
    uid = models.ForeignKey(settings.AUTH_USER_MODEL,
                            on_delete=models.CASCADE, related_name='user')
    is_show = models.BooleanField('是否显示',default=True)
    is_top = models.IntegerField('优先级',default=0)
    article_type = models.IntegerField('文章类型',choices=select_type,null=True,default=None,blank=True)
    updateTime = models.DateTimeField('更新时间', auto_now=True)
    createTime = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = '文章'

    def __str__(self):
        return self.title


class comments(models.Model):
    aid = models.ForeignKey(
        'article', on_delete=models.CASCADE, related_name='article')
    comm_uid = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='评论者',
                                 on_delete=models.CASCADE, related_name='comment_user_id')

    to_comm_uid = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='被回复的人',
                                 on_delete=models.CASCADE,null=True,blank=True,related_name='to_comment_user_id')
    comm_content = models.TextField('评论内容', default='')
    is_show = models.BooleanField('是否显示',default=True)
    updateTime = models.DateTimeField('更新时间', auto_now=True)
    createTime = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = '评论'

    def __str__(self):
        return str(self.aid)


class notify(models.Model):
    is_read = models.IntegerField(
        '是否已读', choices=((1, '已读'), (0, '未读')), default=0)
    content = models.TextField('通知内容')
    aid = models.IntegerField('文章id/为0时管理员通知', default=0)
    uid = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,verbose_name='接收者')
    updateTime = models.DateTimeField('更新时间', auto_now=True)
    createTime = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = '消息通知'


class fineLink(models.Model):
    linkname = models.CharField('链接名称', max_length=20)
    linkurl = models.URLField('链接url', max_length=100)
    updateTime = models.DateTimeField('更新时间', auto_now=True)
    createTime = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = '友情链接'

    def __str__(self):
        return self.linkname


class category(models.Model):
    name = models.CharField('笔记名称', max_length=20)
    desc = models.TextField('描述',null=True,blank=True)
    create_user  = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,verbose_name='创建者')
    book_url = models.URLField('封面链接',null=True,blank=True)
    ad_url = models.URLField('封面广告图片链接',null=True,blank=True)
    ad_name = models.URLField('广告标语',null=True,blank=True)
    updateTime = models.DateTimeField('更新时间', auto_now=True)
    createTime = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = '笔记分类'

    def __str__(self):
        return self.name