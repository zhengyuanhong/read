from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
class websiteMiddleware(MiddlewareMixin):
    def process_request(self, request):
        dic = {
            'welcome':settings.WELCOME,
            'webname':settings.WEB_NAME,
            'author':settings.AUTHOR,
            'icp':settings.ICP,
            'keywords':settings.KEYWORDS,
            'desc':settings.DESC,
            'host':settings.HOST_URL,
            'webtitle':settings.WEB_TITLE 
            }
        request.web = dic
            

    