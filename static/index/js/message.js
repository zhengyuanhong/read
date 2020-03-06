layui.use(['jquery'], function () {
    var $ = layui.jquery
    $.ajax({
      url: '/account/msg',
      method: 'get',
      dataType: 'JSON',
      success: function (res) {
        if (res.code == 200) {
          if (res.data.length > 0) {
            $.each(res.data, function (index, value) {
              var str = '<li data-id="123">' + value.time + '  文章<a href="/detail/' + value.article_id + '?type=message" target="_blank"><cite>' + value.title + '</cite></a>新增一条回复    <a style="color:red;" href="del_msg?id=' + value.id + '">删除</a></li>'
              if (value.article_id == 0) {
                str = '<li data-id="123">' + value.time + '   【管理员】通知：<article style="color: grey;" >' + value.title + '</article><a style="color:red;" href="del_msg?id=' + value.id + '">删除</a></li>'
              }
              $('#message').append(str)
            })
          } else {
            $('#message').append('<div class="fly-none" style="min-height: 50px; padding:30px 0; height:auto;"><span>暂无消息</span></div>')
          }
        }
      }
    });
  });
