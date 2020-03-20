from django.db.models.signals import post_save
from .models import comments, notify, article
from account.models import siteUser
from django.dispatch import receiver


@receiver(post_save, sender=comments)
def comment_notify(sender, instance, created, **kwargs):
    if created:
        aid = instance.aid_id
        comm_uid = instance.comm_uid_id
        to_comm_uid = instance.to_comm_uid_id
        articleInfo = article.objects.filter(id=aid).first()
        author = articleInfo.uid
        title = articleInfo.title
        # 文章作者不给消息通知
        if comm_uid != articleInfo.uid_id and not to_comm_uid:
            content = '你发布的  ”'+title+'“ 新增一条评论'
            notify.objects.create(is_read=0, uid=author, content=content, aid=aid)

        if to_comm_uid:
            userInfo = siteUser.objects.filter(id=comm_uid).first()
            content = userInfo.username +'在  ”'+title+'“  中回复了你' 
            notify.objects.create(is_read=0, uid_id=to_comm_uid, content=content, aid=aid)