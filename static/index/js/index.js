layui.use(['form', 'jquery', 'layer'], function () {
  var form = layui.form
  var $ = layui.jquery
  var layer = layui.layer
  var book_list = $('#book_list')
  var user_login = $('#user_login')
  form.on('submit(create)', function (data) {
    $.ajax({
      url: '/create',
      method: 'post',
      data: data.field,
      dataType: 'JSON',
      success: function (res) {
        if (res.code == 200) {
          layer.msg((res.msg));
          var str = "<dd><a href='?note=" + res.data[0].id + "'>" + res.data[0].name + "</a><dd>"
          book_list.append(str)
          $('#input_val').val('')
          $('#text_val').val('')
        } else {
          layer.msg(res.msg);
        }
      }
    });
    return false
  })

  // $.ajax({
  //   url: '/user-login',
  //   method: 'get',
  //   dataType: 'JSON',
  //   success: function (res) {
  //     if (res.code == 200) {
  //       var str = ''
  //       res.data.forEach(function (value, index) {
  //         str = "<dd><a href='account/u/" + value.id + "'><img src='" + value.avatar + "'><i>" + value.username + "</i></a></dd>"
  //         user_login.append(str)
  //       })
  //     } else {
  //       layer.msg(res.msg);
  //     }
  //   }
  // });

});