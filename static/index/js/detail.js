layui.use(['jquery', 'form'], function () {
  var $ = layui.jquery
  var form = layui.form
  // 文章详情
  var article = $('#article_detail').text()
  $('#article_detail').html(article)
  var length = $('#jieda > li').length

  for (var i = parseInt(length); i > 0; i--) {
    var reply = $(".reply_content[data-id=" + i + "]").text();
    $(".reply_content[data-id=" + i + "]").html(reply);
  }

  //回复功能
  $('span.reply_btn').click(function () {
    console.log('ddd')
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
      success: function (res) {
        $('#L_content').val('')
        if (res.code == 200) {
          layer.msg((res.msg));
          var value = res.data[0]
           var reply_content = `<li data-id="${value.user.id}" class="jieda-daan">
    <div class="detail-about detail-about-reply" >
      <a class="fly-avatar" href="/account/u/${value.user.id}">
        <img src="${value.user.avatar}" alt="${value.user.username}">
            </a>
        <div class="fly-detail-user">
          <a href="/account/u/${value.user.id}" class="fly-link">
            <cite>${ value.user.username}</cite>
          </a>
        </div>

        <div class="detail-hits">
          <span>${ value.comm_time}</span>
        </div>

          </div>
      <div class="detail-body jieda-body photos">
        <p class="reply_content" data-id=${ value.index} >${value.comm_content}</p>
      </div>
      <div class="jieda-reply">
        <span class="reply_btn" data-username='${value.user.username}' id='${value.user.id}' type="reply">
          <i class="iconfont icon-svgmoban53"></i>
              回复
        </span>
      </div>
     </li>`
          $('#jieda').append(reply_content)
          // window.location.reload();
        } else {
          layer.msg(res.msg);
        }
      }
    });
    return false
  })
});