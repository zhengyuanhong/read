from django.db.models.signals import post_save
from .models import comments, notify, article
from django.dispatch import receiver


@receiver(post_save, sender=comments)
def comment_notify(sender, instance, created, **kwargs):
    if created:
        aid = instance.aid_id
        articleInfo = article.objects.filter(id=aid).first()
        author = articleInfo.uid
        title = articleInfo.title
        notify.objects.create(is_read=0, uid=author, content=title, aid=aid)
