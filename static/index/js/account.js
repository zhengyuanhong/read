layui.use(['jquery'], function () {
  var $ = layui.jquery
  var user_id = $('#user_id').attr('data')
  $.ajax({
    url: 'article',
    method: 'get',
    data: { userid: user_id },
    dataType: 'JSON',
    success: function (res) {
      if (res.code == 200) {
        if (res.data.length > 0) {
          $.each(res.data, function (index, value) {
            var str = '<li><a href="/detail/' + value.id + '" class="jie-title"><span class="layui-badge layui-bg-gray">' + value.book_name + '</span>' + value.title + '</a><i>' + value.time + '</i><em class="layui-hide-xs">' + value.comm_num + '条评论</em></li>'
            $('#user_article').append(str)
          })
        } else {
          $('#user_article').append('<div class="fly-none" style="min-height: 50px; padding:30px 0; height:auto;"><span>已经到底了</span></div>')
          $('#moreArticle').hide()
        }
      }
    }
  });

  var article_page = 1
  $('#moreArticle').click(function () {
    article_page += 1
    $.ajax({
      url: 'article',
      method: 'get',
      data: { userid: user_id, page: article_page },
      dataType: 'JSON',
      success: function (res) {
        if (res.code == 200) {
          if (res.data.length > 0) {
            $.each(res.data, function (index, value) {
              var str = '<li><a href="/detail/' + value.id + '" class="jie-title"><span class="layui-badge layui-bg-gray">' + value.book_name + '</span>' + value.title + '</a><i>' + value.time + '</i><em class="layui-hide-xs">' + value.comm_num + '条评论</em></li>'
              $('#user_article').append(str)
            })
          } else {
            layer.msg('已经到底了')
          }
        }
      }
    });
  })

  $.ajax({
    url: 'comment',
    method: 'get',
    data: { userid: user_id },
    dataType: 'JSON',
    success: function (res) {
      if (res.code == 200) {
        if (res.data.length > 0) {
          $.each(res.data, function (index, value) {
            var str = '<li><p><span>' + value.time + '</span>在<a href="/detail/' + value.article_id + '" target="_blank">' + value.article_title + '</a>参与评论</p></li>'
            $('#user_comment').append(str)
          })
        } else {
          $('#user_comment').append('<div class="fly-none" style="min-height: 50px; padding:30px 0; height:auto;"><span>已经到底了</span></div>')
            $('#moreComment').hide()
        }
      }
    }
  });

  var comment_page = 1
  $('#moreComment').click(function () {
    comment_page+=1
    $.ajax({
      url: 'comment',
      method: 'get',
      data: { userid: user_id,page:comment_page },
      dataType: 'JSON',
      success: function (res) {
        if (res.code == 200) {
          if (res.data.length > 0) {
            $.each(res.data, function (index, value) {
              var str = '<li><p><span>' + value.time + '</span>在<a href="/detail/' + value.article_id + '" target="_blank">' + value.article_title + '</a>参与评论</p></li>'
              $('#user_comment').append(str)
            })
          } else {
            layer.msg('已经到底了')
          }
        }
      }
    });
  })
});

