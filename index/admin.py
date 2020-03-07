from django.contrib import admin
from .models import category,comments,article,fineLink,notify
from django.conf import settings

@admin.register(category)
class categoryAdmin(admin.ModelAdmin):
    list_display = ('id','name','create_user','book_url','updateTime','createTime')
    list_display_links = ('name','create_user','book_url')

@admin.register(comments)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','aid','comm_uid','comm_content','updateTime','createTime')

@admin.register(article)
class articleAdmin(admin.ModelAdmin):
    list_display=('id','title','uid','content','category','is_top','is_show','updateTime','createTime')
    list_display_links = ('title','content')
    list_editable = ('is_top','category')
    search_fields = ('title','content')

@admin.register(notify)
class notifyAdmin(admin.ModelAdmin):
    list_display=('id','uid','aid','content','is_read','updateTime','createTime')
    list_display_links = ('content',)
    search_fields = ('aid',)
    list_editable = ('is_read',)

@admin.register(fineLink)
class fineLinkAdmin(admin.ModelAdmin):
    list_display=('id','linkurl','linkname','updateTime','createTime')
    list_display_links = ('linkname',)
    list_editable = ('linkurl',)

#修改网页title和站点header。
admin.site.site_title = settings.WEB_NAME+"后台管理"
admin.site.site_header = settings.WEB_NAME
