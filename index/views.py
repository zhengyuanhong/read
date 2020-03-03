from django.shortcuts import render
from django.http import request, HttpResponse, JsonResponse, HttpResponseRedirect
from django.conf import settings
from django.core.cache import cache
from account.models import siteUser
from django.core.paginator import Paginator
from .models import article, comments, category as cate, notify
from django.contrib.auth.decorators import login_required
from utils.util import addJiFen, reduceJiFen, formateTime
import datetime
# Create your views here.


def index_page_not_found(request):
    return render(request, '404.html')


def index(request):
    if request.method == 'GET':
        category = request.GET.get('category', 0)
        page_id = request.GET.get('page', 1)
        if int(page_id) <= 0 or int(category) < 0:
            page_id = 1
            category = 0

        if int(category) == 0:
            art = article.objects.filter(
                is_show=True).all().order_by('-is_top','-createTime')
        else:
            art = article.objects.filter(category=category).filter(
                is_show=True).all().order_by('-is_top','-createTime')

        # 分页显示，把status 的数据按照3个一页显示
        paginator = Paginator(art, 20)
        # 获取第一页的内容
        page = paginator.page(page_id)

        # 更具分类category 获取首页数据
        data = []
        for i in page:
            temp = {}
            temp['id'] = i.id
            temp['title'] = i.title
            temp['user'] = i.uid
            temp['createTime'] = formateTime(
                str(i.createTime.strftime("%Y-%m-%d %H:%M:%S")))
            temp['comm_num'] = i.article.count()
            temp['is_top'] = i.is_top
            data.append(temp)

        # 最近注册
        userRich = siteUser.objects.all().order_by('-last_login')[0:16]

        richdata = []
        for u in userRich:
            temp = {}
            temp['id'] = u.id
            temp['username'] = u.username
            temp['avatar'] = u.avatar
            temp['jifen'] = u.jifen
            richdata.append(temp)

        context = {}
        context['art'] = data
        context['rich'] = richdata
        context['page'] = page
        context['cate'] = cate.objects.order_by('categoryId')
        context['category_id'] = int(category)
        return render(request, 'index/index.html', context)


def detail(request, article_id):
    types = request.GET.get('type')
    detail = article.objects.filter(id=article_id).first()  # 获取文章详情

    if not detail:
        return render(request, '404.html',{'tip':'该文章已被作者删除'})

    if not detail.is_show:
        return render(request, '404.html',{'tip':'该文章已违规，已被管理员删除'})

    comment = comments.objects.filter(aid=detail)
    comm_num = comment.count()  # 获取评论条数
    author = detail.uid  # 获取作者信息

    if types == 'message':
        n = notify.objects.filter(aid=article_id).first()
        n.is_read = 1
        n.save()

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

    return render(request, 'index/detail.html', {'detail': detail, 'author': author, 'comm_num': comm_num, 'data': data})


@login_required
def postAdd(request):
    if request.method == 'GET':
        # 如果积分少于15，就不能发布文章
        if request.user.jifen <= settings.QUAN_XIAN:
            return render(request, 'refuse_write.html',{'tip':'你的财富值不够发表文章，去评论其他文章可获得更多财富'})

        now = datetime.datetime.now() 
        count = article.objects.filter(uid=request.user).filter(createTime__year=now.year,createTime__month=now.month,createTime__day=now.day).count()
        # 每个账号每天只能发布五篇文章
        if count >= settings.MAX_NUM:
            return render(request, 'refuse_write.html',{'tip':'你今天已经发布了{}篇文章，明天再来吧'.format(settings.MAX_NUM)})

        # 数字转中文
        intTozh={
            1:'一',
            2:'两',
            3:'三',
            4:'四',
            5:'五',
        }
        num = intTozh[settings.MAX_NUM-count]
        data = cate.objects.all()
        return render(request, 'index/add.html', {'data': data,'num':num})

    if request.method == 'POST':
        category = request.POST.get('category')
        title = request.POST.get('title')
        content = request.POST.get('content')

        if not title:
            return JsonResponse({'code': 201, 'msg': '内容不能为空'})

        if not content:
            return JsonResponse({'code': 201, 'msg': '内容不能为空'})

        article.objects.create(
            category=category, title=title, content=content, uid=request.user)
        # 发布文章增加5个积分
        addJiFen(request, settings.ADD_JIFEN)

        return JsonResponse({'code': 200, 'msg': '发布成功'})


@login_required
def editArticle(request, article_id):
    if request.method == 'GET':
        detail = article.objects.filter(
            id=article_id, uid_id=request.user.id).first()
        catedata = cate.objects.all()
        article_cate = cate.objects.filter(categoryId=detail.category).first()

        context = {}
        context['id'] = detail.id
        context['cate'] = article_cate
        context['title'] = detail.title
        context['content'] = detail.content
        context['catedata'] = catedata
        return render(request, 'index/edit.html', context)

    if request.method == 'POST':
        category = request.POST.get('category')
        title = request.POST.get('title')
        content = request.POST.get('content')

        if not title:
            return JsonResponse({'code': 201, 'msg': '内容不能为空'})

        if not content:
            return JsonResponse({'code': 201, 'msg': '内容不能为空'})

        detail = article.objects.filter(id=request.POST.get(
            'aid'), uid_id=request.user.id).first()
        detail.category = category
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

        comments.objects.create(
            aid_id=aid, comm_uid_id=request.user.id, comm_content=content)

        # 增加评论积分
        addJiFen(request, settings.ADD_REPLAY_JIFEN) 

        # TODO 去通知作者 有人评论评论帖子
        articleInfo = article.objects.filter(id=aid).first()
        author = articleInfo.uid
        title = articleInfo.title
        notify.objects.create(is_read=0, uid=author, content=title, aid=aid)
        return JsonResponse({'code': 200, 'msg': '发布成功'})


@login_required
def uploadImage(request):
    pass

# 获取前十二名财富上榜
@login_required
def getUserRank(request):
    pass
