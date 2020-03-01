from django.utils.deprecation import MiddlewareMixin
from index.models import notify


class notifyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            #通知显示
            request.is_notify = notify.objects.filter(uid=request.user,is_read=0).exists()
        else:
            return False