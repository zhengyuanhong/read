from django.contrib import admin
from .models import category,comments,article,fineLink

@admin.register(category)
class categoryAdmin(admin.ModelAdmin):
    list_display = ('id','name','categoryId','updateTime','createTime')
    list_editable = ('name',)
@admin.register(comments)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','aid','comm_uid','comm_content','updateTime','createTime')


@admin.register(article)
class articleAdmin(admin.ModelAdmin):
    list_display=('id','title','uid','content','is_show','updateTime','createTime')
    list_display_links = ('title','content')
#修改网页title和站点header。
admin.site.site_title = "X社区后台管理"
admin.site.site_header = "X社区"
