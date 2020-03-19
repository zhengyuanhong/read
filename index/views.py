from django.shortcuts import render
from django.http import request, HttpResponse, JsonResponse, HttpResponseRedirect
from django.conf import settings
from django.core.cache import cache
from account.models import siteUser
from django.core.paginator import Paginator
from .models import article, comments, category as cate, notify, fineLink
from django.contrib.auth.decorators import login_required
from utils.util import addJiFen, reduceJiFen, formateTime, getlevel
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.db.models import Count
# Create your views here.


def index_page_not_found(request):
    return render(request, '404.html')


def index(request):
    if request.method == 'GET':
        category = int(request.GET.get('category', 0))
        page_id = request.GET.get('page', 1)
        if int(page_id) <= 0:
            page_id = 1

        if category == 0:
            art = article.objects.filter(
                is_show=True).all().order_by('-is_top', '-createTime')
        else:
            art = article.objects.filter(category_id=category).filter(
                is_show=True).all().order_by('-is_top', '-createTime')

        # 分页显示，把status 的数据按照3个一页显示
        paginator = Paginator(art, 20)
        # 获取第一页的内容
        page = paginator.page(page_id)

        # 更具分类category 获取首页数据
        article_data = []
        for i in page:
            temp = {}
            temp['id'] = i.id
            temp['title'] = i.title
            temp['user'] = i.uid
            temp['createTime'] = formateTime(
                str(i.createTime.strftime("%Y-%m-%d %H:%M:%S")))
            temp['comm_num'] = i.article.count()
            temp['is_top'] = i.is_top
            temp['category'] = i.category.name if i.category else '综合'
            temp['category_id'] = i.category.id if i.category else 0
            article_data.append(temp)

        context = {}
        context['article'] = article_data
        context['page'] = page
        context['cate'] = cate.objects.all()
        context['fineurl'] = fineLink.objects.all()
        # 查询 每本书名下的文章数量
        context['hot'] = cate.objects.annotate(post_num=Count('article')).filter(
            post_num__gt=0).order_by('-post_num')[0:10]
        return render(request, 'index/index.html', context)


def detail(request, article_id):
    detail = article.objects.filter(id=article_id).first()  # 获取文章详情

    if not detail:
        return render(request, '404.html', {'tip': '该文章已被作者删除'})

    if not detail.is_show:
        return render(request, '404.html', {'tip': '该文章已违规，已被管理员删除'})

    comment = comments.objects.filter(aid=detail)
    comm_num = comment.count()  # 获取评论条数
    author = detail.uid  # 获取作者信息

    data = []
    index = 0
    for m in comment.all():
        index += 1
        temp = {}
        temp['index'] = index
        temp['user'] = m.comm_uid
        temp['comm_content'] = m.comm_content
        temp['comm_time'] = formateTime(
            str(m.createTime.strftime("%Y-%m-%d %H:%M:%S")))
        data.append(temp)

    context = {
        'detail': detail,
        'author': author,
        'comm_num': comm_num,
        'data': data
    }

    return render(request, 'index/detail.html', context)


@login_required
def createCategory(request):
    if request.method == 'POST':
        book_name = request.POST.get('book_name')
        if not book_name:
            return JsonResponse({'code': 201, 'msg': '内容不能为空'})

        exits = cate.objects.filter(name=book_name).exists()
        if exits:
            return JsonResponse({'code': 201, 'msg': '已经存在'})

        name = cate.objects.create(name=book_name, create_user=request.user)
        return JsonResponse({'code': 200, 'msg': '创建成功','data':[{'id':name.id,'name':name.name}]})


@login_required
def postAdd(request):
    if request.method == 'GET':
        # 获取发布文章次数
        # res = getlevel(request)
        # 如果获取次数，则限制次数
        # num = 0
        # if res != 0:
        #     now = datetime.datetime.now()
        #     count = article.objects.filter(uid=request.user).filter(
        #         createTime__year=now.year, createTime__month=now.month, createTime__day=now.day).count()
            # 每个账号每天只能发布res篇文章
            # if count >= res:
            #     return render(request, 'refuse_write.html', {'tip': '你今天已经发布了{}篇文章，明天再来吧'.format(res)})

            # 数字转中文
        #     intTozh = {
        #         1: '一',
        #         2: '两',
        #         3: '三',
        #         4: '四',
        #         5: '五',
        #     }
        #     num = intTozh[res-count]
        # else:
        #     num = 0
        category = cate.objects.all()
        return render(request, 'index/add.html', {'cate': category})

    if request.method == 'POST':
        category = request.POST.get('category')
        title = request.POST.get('title')
        content = request.POST.get('content')

        if not title:
            return JsonResponse({'code': 201, 'msg': '内容不能为空'})

        if not content:
            return JsonResponse({'code': 201, 'msg': '内容不能为空'})

        article.objects.create(
            category_id=category, title=title, content=content, uid=request.user)
        # 发布文章增加5个积分
        addJiFen(request, settings.ADD_JIFEN)

        return JsonResponse({'code': 200, 'msg': '发布成功'})


@login_required
def editArticle(request):
    if request.method == 'GET':
        detail = article.objects.filter(
            id=request.GET.get('aid'), uid_id=request.user.id).first()

        context = {}
        context['id'] = detail.id
        context['category_name'] = detail.category.name if detail.category else '综合' 
        context['category_id'] = detail.category.id if detail.category else None
        context['title'] = detail.title
        context['content'] = detail.content
        return render(request, 'index/edit.html', context)

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        if not title:
            return JsonResponse({'code': 201, 'msg': '内容不能为空'})

        if not content:
            return JsonResponse({'code': 201, 'msg': '内容不能为空'})

        detail = article.objects.filter(id=request.POST.get(
            'aid'), uid_id=request.user.id).first()

        detail.title = title
        detail.content = content
        detail.save()
        return JsonResponse({'code': 200, 'msg': '更新成功'})


@login_required
def deleteArticle(request):
    if request.method == 'GET':
        article_id = request.GET.get('id')
        # 扣除积分
        res = reduceJiFen(request, settings.REDUCE_JIFEN)
        if not res:
            return JsonResponse({'code': 201, 'msg': '财富不够'})

        article.objects.get(id=article_id).delete()

        return JsonResponse({'code': 200, 'msg': '删除成功'})


@login_required
def postReply(request):
    if request.method == 'POST':
        aid = request.POST.get('aid')
        content = request.POST.get('content')
        contentlist = content.split(' ', 1)

        userinfo = siteUser.objects.filter(username=contentlist[0][1:]).first()
        if userinfo:
            content = '<a href="/account/u/{userid}">@{username}</a> {content}'.format(
                userid=userinfo.id, username=userinfo.username, content=contentlist[1:][0])
        
            if request.user.id == userinfo.id:
                return JsonResponse({'code': 201, 'msg': '不能给自己评论'})

        comments.objects.create(
            aid_id=aid, comm_uid_id=request.user.id, comm_content=content)

        # 增加评论积分
        addJiFen(request, settings.ADD_REPLAY_JIFEN)
        return JsonResponse({'code': 200, 'msg': '评论成功'})


@login_required
def uploadImage(request):
    pass

# 获取最近登陆的用户
def getUserLogin(request):
    if request.method == 'GET':
        userLogin = siteUser.objects.all().order_by('-last_login')[0:16]

        data = []
        for u in userLogin:
            temp = {}
            temp['id'] = u.id
            temp['username'] = u.username
            temp['avatar'] = u.avatar
            data.append(temp) 
        
        context = {}
        context['code'] = 200
        context['msg'] = 'sueecss'
        context['data']=data
        return JsonResponse(context) 