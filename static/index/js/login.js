layui.use(['form', 'jquery'], function () {
    var form = layui.form,
      $ = layui.jquery

    form.on('submit(login)', function (data) {
      $.ajax({
        url: 'login',
        method: 'post',
        data: data.field,
        dataType: 'JSON',
        success: function (res) {
          if (res.code == 200) {
            layer.msg((res.msg));
            setTimeout(function(){
              window.location.href = "/"
            },500)
          } else if (res.code == 202) {
            layer.msg(res.msg);
            $("#tip").html('<a href="verif_email" style="text-decoration: underline;">点击去验证邮箱</a>')
          } else {
            layer.msg(res.msg);
          }
        }
      })
      return false
    });
  });