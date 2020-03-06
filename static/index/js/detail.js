layui.use(['jquery', 'form'], function () {
    var $ = layui.jquery
    var form = layui.form
    // 文章详情
    var article = $('#article_detail').text()
    $('#article_detail').html(article)

    for (var i = parseInt("{{data|length}}"); i > 0; i--) {
      var reply = $(".reply_content[data-id=" + i + "]").text();
      $(".reply_content[data-id=" + i + "]").html(reply);
    }


    //回复功能
    $('span.reply_btn').click(function () {
      var str = '@' + $(this).attr('data-username') + ' '
      $('#L_content').val(str)
      $("#L_content").focus();
    })

    form.on('submit(reply)', function (data) {
      $.ajax({
        url: 'reply',
        method: 'post',
        data: data.field,
        dataType: 'JSON',
        async : false,
        success: function (res) {
          $('#L_content').val('')
          if (res.code == 200) {
            layer.msg((res.msg));
              window.location.reload();
          } else {
            layer.msg(res.msg);
          }
        }
      });
      return false
    })

    $('#delete').click(function () {
      var aid = $(this).attr('data')
      $.ajax({
        url: '/detail/delete',
        method: 'get',
        data: {
          id:aid
        },
        dataType: 'JSON',
        async : false,
        success: function (res) {
          if (res.code == 200) {
            layer.msg((res.msg));
            setTimeout(function(){
              window.location.href = "/"
            },500)
          } else {
            layer.msg(res.msg);
          }
        }
      });
    })
  });