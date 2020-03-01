from django.db import models
from django.conf import settings


class article(models.Model):
    title = models.CharField('标题', max_length=50)
    content = models.TextField('内容')
    category = models.IntegerField('分类id', default=0)
    uid = models.ForeignKey(settings.AUTH_USER_MODEL,
                            on_delete=models.CASCADE, related_name='user')
    is_show = models.BooleanField('是否显示',default=True)
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
    comm_content = models.TextField('评论内容', default='')
    updateTime = models.DateTimeField('更新时间', auto_now=True)
    createTime = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = '评论'

    def __str__(self):
        return self.aid


class notify(models.Model):
    is_read = models.IntegerField(
        '是否已读', choices=((1, '已读'), (0, '未读')), default=0)
    content = models.CharField('内容', max_length=50)
    aid = models.IntegerField('文章id', default=0)
    uid = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    updateTime = models.DateTimeField('更新时间', auto_now=True)
    createTime = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = '评论通知'


class fineLink(models.Model):
    linkname = models.CharField('链接名称', max_length=10)
    linkurl = models.CharField('链接url', max_length=100)
    updateTime = models.DateTimeField('更新时间', auto_now=True)
    createTime = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = '友情链接'

    def __str__(self):
        return self.linkname


class category(models.Model):
    name = models.CharField('分类名称', max_length=10)
    categoryId = models.IntegerField('分类下标', default=0)
    updateTime = models.DateTimeField('更新时间', auto_now=True)
    createTime = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = '分类'

    def __str__(self):
        return self.name
