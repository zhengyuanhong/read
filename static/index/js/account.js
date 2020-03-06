layui.use(['jquery'], function () {
    var $ = layui.jquery
    var user_id = $('#user_id').attr('data')
    $.ajax({
      url: 'article',
      method: 'get',
      data: {userid:user_id},
      dataType: 'JSON',
      success: function (res) {
        if (res.code == 200) {
          if (res.data.length > 0) {
            $.each(res.data, function (index, value) {
              var str = '<li><a href="/detail/' + value.id + '" class="jie-title"><span class="layui-badge layui-bg-gray">'+value.book_name+'</span>'+value.title + '</a><i>' + value.time + '</i><em class="layui-hide-xs">' + value.comm_num + '条评论</em></li>'
              $('#user_article').append(str)
            })
          } else {
            $('#user_article').append('<div class="fly-none" style="min-height: 50px; padding:30px 0; height:auto;"><span>没写任何东西</span></div>')
          }
        }
      }
    });

    $.ajax({
      url: 'comment',
      method: 'get',
      data: {userid:user_id},
      dataType: 'JSON',
      success: function (res) {
        if (res.code == 200) {
          if (res.data.length > 0) {
            $.each(res.data, function (index, value) {
              var str = '<li><p><span>'+value.time+'</span>在<a href="/detail/'+value.article_id+'" target="_blank">'+value.article_title+'</a>参与评论</p></li>'
              $('#user_comment').append(str)
            })
          } else {
            $('#user_comment').append('<div class="fly-none" style="min-height: 50px; padding:30px 0; height:auto;"><span>没有参与任何评论</span></div>')
          }
        }
      }
    });
  });

  