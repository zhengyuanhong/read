from django.contrib import admin
from .models import category,comments,article,fineLink

@admin.register(category)
class categoryAdmin(admin.ModelAdmin):
    list_display = ('id','name','categoryId','updateTime','createTime')

@admin.register(comments)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','aid','comm_uid','comm_content','updateTime','createTime')


@admin.register(article)
class articleAdmin(admin.ModelAdmin):
    list_display=('id','title','uid','content','updateTime','createTime')
    
#修改网页title和站点header。
admin.site.site_title = "X社区后台管理"
admin.site.site_header = "X社区"
