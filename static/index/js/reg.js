layui.use(['form', 'jquery'], function () {
    var form = layui.form,
      $ = layui.jquery

    form.on('submit(register)', function (data) {
      $.ajax({
        url: 'register',
        method: 'post',
        data: data.field,
        dataType: 'JSON',
        success: function (res) {
          if (res.code == 200) {
            layer.msg((res.msg));
            setTimeout(function () {
              window.location.href = "email_tip"
            }, 500)
          } else {
            layer.msg(res.msg);
          }
        }
      });
      return false
    });
  });