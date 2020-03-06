"""readDjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.views.static import serve
import account
from django.contrib import admin
from django.urls import path, include, re_path
from index.views import index, getUserRank, detail, \
    postAdd, uploadImage, postReply, editArticle,\
    deleteArticle, index_page_not_found, createCategory

urlpatterns = [
    path('read_admin/', admin.site.urls),
    path('', index, name='index'),
    path('detail/<int:article_id>', detail, name='detail'),
    path('detail/edit', editArticle, name='editArticle'),
    path('detail/reply', postReply, name='postReply'),
    path('detail/delete', deleteArticle, name='deleteArticle'),
    path('add', postAdd, name='postAdd'),
    path('create', createCategory, name='createCategory'),
    path('upload', uploadImage, name='uploadImage'),
    path('account/', include('account.urls')),
    path('rank', getUserRank),
    re_path(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT})
]

handler404 = account.views.page_not_found
handler500 = account.views.page_not_found
handler404 = index_page_not_found
handler500 = index_page_not_found
